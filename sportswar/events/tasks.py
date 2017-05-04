import logging
import pytz

from allauth.account.models import EmailAddress

from celery.decorators import periodic_task, task
from celery.task.schedules import crontab

from django.conf import settings
from django.utils import timezone

from smsish.sms import send_sms
from sportswar.events.models import Alert, Event, Scheduler
from sportswar.users.models import User
from sportswar.users.serializers import UserSerializer
from sportswar.utils.build_db import create_events_for_all_teams
from sportswar.utils.emails import prepare_and_send_email

logger = logging.getLogger(__name__) 

SCHEDULE_HOURS_AHEAD = 25


def humanize_datetime(gametime, tzone):
    try:
        adjusted = gametime.astimezone(pytz.timezone(tzone))
        humanized = adjusted.strftime('%A at %-I:%M%p')
        humanized += ' {}'.format(tzone)
    except pytz.UnknownTimeZoneError:
        humanized = gametime.strftime('%A at %-I:%M%p UTC')
    return humanized


@task(name="send_alert_email")
def send_alert_email(event_details):
    prepare_and_send_email('watcher_alert', event_details)


@task(name="send_alert_sms")
def send_alert_sms(details):

    from_number = settings.TWILIO_FROM_NUMBER

    try:
        user = details['user']
        recipients = (user['phone_number'],)
        email = user['email']
    except KeyError:
        logger.error('SMS alert details missing phone number! - %s', details)
        return

    try:
        team = details.get('team_name', 'your team')
        loc = details.get('location', None)
        gtime = details.get('gametime', None)
        ana = 'an' if loc == 'away' else 'a'
        msg = 'Sports Warning! {team} are playing {ana} {loc} game {gtime}.'.format(team=team, ana=ana, loc=loc, gtime=gtime)
    except KeyError:
        logger.error('KeyError in sms alert %s', details)
        msg = 'Sports Warning! One of your warnings was triggered but we failed.  Look out for sports today!'
    msg += ' - sportswarning.com via {}'.format(email)
    send_sms(msg, from_number, recipients)


@periodic_task(
    run_every=(crontab(minute='*/15')),
    name="schedule_alerts",
    ignore_result=True
)
def schedule_alerts():
    scheduler = Scheduler.objects.first()
    scheduler.create_alerts(SCHEDULE_HOURS_AHEAD)


@periodic_task(
    run_every=(crontab(minute='*/10')),
    name="check_for_alerts",
    ignore_result=True
)
def check_for_alerts():
    scheduler = Scheduler.objects.first()
    scheduler = Scheduler.objects.first()
    if scheduler.last_alerted:
        start_time = scheduler.last_alerted
    else:
        start_time = timezone.now()
    end_time = timezone.now() + timezone.timedelta(minutes=20)
    alerts = Alert.objects.filter(alert_time__gte=start_time,
                                  alert_time__lt=end_time,
                                  sent=False).prefetch_related('watcher').prefetch_related('event').prefetch_related('user')
    for alert in alerts:
        watcher = alert.watcher
        details = alert.event.get_details()
        user = alert.user
        details['user'] = UserSerializer(user).data
        details['gametime'] = humanize_datetime(details['gametime'], user.time_zone)

        logger.info('Sending alert = %s', details)
        if watcher.notification_method in ['email', 'both']:
            send_alert_email.delay(details)
        if watcher.notification_method in ['sms', 'both']:
            if user.phone_number and user.has_validated_phone:
                send_alert_sms.delay(details)
        alert.sent = True
        alert.save()
    scheduler.last_alerted = timezone.now()
    scheduler.save()


@periodic_task(
    run_every=(crontab(minute=0, hour=5)),  # crontab(minute=0, hour=5) to run every day midnight EST
    name="check_for_events",
    ignore_result=True
)
def check_for_events():
    create_events_for_all_teams()


@periodic_task(
    run_every=(crontab(minute=0, hour=0)),  # crontab(minute=0, hour=0) to run every day midnight UTC
    name="cleanup_events_alerts_users",
    ignore_result=True
)
def cleanup_events_alerts_users():
    expiration = timezone.now() - timezone.timedelta(days=14)
    events = Event.objects.filter(game_datetime__lt=expiration)
    for event in events:
        logger.info('Deleting past event %s', event)
        event.delete()

    alerts = Alert.objects.filter(alert_time__lt=expiration)
    for alert in alerts:
        logger.info('Deleting past alert %s', alert)
        alert.delete()

    users = User.objects.filter(last_login__isnull=True, date_joined__lt=expiration)
    for user in users:
        try:
            if not user.emailaddress_set.get(email=user.email).verified:
                logger.info('Deleting inactive user %s', user)
                user.delete()
        except EmailAddress.DoesNotExist:
            logger.warning('Email address not found %s.  Attempting to delete anyway', user)
            user.delete()
