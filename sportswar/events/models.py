import logging

from django.db import IntegrityError
from django.db import models
from django.utils import timezone

from sportswar.teams.models import Team
from sportswar.users.models import User


logger = logging.getLogger(__name__)

NOTIFICATION_CHOICES = (
    ('email', 'email'),
    ('sms', 'sms'),
    ('both', 'both')
)

NOTIFICATION_HOUR_CHOICES = ((n, n) for n in range(25))


class Event(models.Model):

    class Meta:
        unique_together = (('team', 'game_datetime', 'seatgeek_id'))

    def __str__(self):
        return ' - '.join([self.team.name, str(self.home), str(self.game_datetime)])

    opponent = models.CharField(max_length=1024)
    game_datetime = models.DateTimeField('game datetime')
    home = models.BooleanField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    seatgeek_id = models.IntegerField(default=0)

    def has_passed(self):
        return self.game_datetime < timezone.now()

    def get_details(self):
        details = {}
        details['location'] = 'home' if self.home else 'away'
        details['team_name'] = self.team.name
        details['gametime'] = self.game_datetime
        return details


class Watcher(models.Model):

    class Meta:
        unique_together = (('team', 'user', 'notification_method', 'hours_before',))

    def __str__(self):
        return ' - '.join([str(self.id), self.team.name, self.user.email])

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchers')
    hours_before = models.IntegerField('Send Hours Before', default=1,
                                       choices=NOTIFICATION_HOUR_CHOICES)
    notification_method = models.CharField('Notification Type', default='email',
                                           choices=NOTIFICATION_CHOICES, max_length=5)
    notify_away_games = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.notification_method in ['sms', 'both'] and not self.user.has_validated_phone:
            self.notification_method = 'email'
        super().save(*args, **kwargs)


class Alert(models.Model):

    def __str__(self):
        return ' - '.join([str(self.id), str(self.watcher), str(self.alert_time)])

    class Meta:
        unique_together = (('watcher', 'event', 'alert_time',))

    alert_time = models.DateTimeField('alert_time')
    watcher = models.ForeignKey(Watcher, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)


class Scheduler(models.Model):

    def __str__(self):
        return ' - '.join([str(self.id), str(self.last_scheduled)])

    last_scheduled = models.DateTimeField(blank=True, null=True)
    last_alerted = models.DateTimeField(blank=True, null=True)

    def create_alerts(self, hours_ahead):
        now = timezone.now()
        if self.last_scheduled:
            start_time = self.last_scheduled
        else:
            start_time = now
        end_time = now + timezone.timedelta(hours=hours_ahead)

        events = Event.objects.filter(game_datetime__gte=start_time, game_datetime__lte=end_time)

        for event in events:
            watchers = Watcher.objects.filter(team=event.team).prefetch_related('user')
            for watcher in watchers:
                alert_time = event.game_datetime - timezone.timedelta(hours=watcher.hours_before)
                if not watcher.notify_away_games and not event.home:
                    continue
                try:
                    Alert.objects.create(watcher=watcher, event=event, user=watcher.user, alert_time=alert_time)
                except IntegrityError:
                    pass
        self.last_scheduled = timezone.now()
        self.save()
        duration = timezone.now() - now
        logger.info('Create alerts finished.  Time elapsed: %s', duration)
