import datetime

from collections import OrderedDict

from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from authy.api import AuthyApiClient

from django.core import mail
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
from django.test import TestCase, RequestFactory
from django.urls import reverse

from unittest.mock import patch
from unittest.mock import MagicMock

from rest_framework.test import APIClient, APIRequestFactory, APITestCase, RequestsClient
from rest_framework.exceptions import ValidationError
# RequestsClient is good for testing live environment, requires fully qualified urls
from sportswar.events.models import Alert, Event, Scheduler, Watcher
from sportswar.teams.models import Team, League
from sportswar.users.models import User


def create_leagues():
    League.objects.get_or_create(name='nfl')
    League.objects.get_or_create(name='mlb')

def create_teams():
    nfl = League.objects.get(name='nfl')
    mlb = League.objects.get(name='mlb')
    Team.objects.get_or_create(name='Huffies', slug='huffies', league=nfl)
    Team.objects.get_or_create(name='Jerk Shoes', slug='jerk-shoes', league=nfl)
    Team.objects.get_or_create(name='Dog Balls', slug='dog-balls', league=mlb)
    Team.objects.get_or_create(name='Taco Trucks', slug='taco-trucks', league=mlb)

def create_watchers(user):
    team = Team.objects.first()
    Watcher.objects.get_or_create(user=user, team=team, hours_before=1, notification_method='email', notify_away_games=False)
    team = Team.objects.last()
    Watcher.objects.get_or_create(user=user, team=team, hours_before=2, notification_method='email', notify_away_games=True)


class BaseAPITests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseAPITests, cls).setUpClass()
        cls.factory = APIRequestFactory()
        cls.client = APIClient()
        cls.user1, _ = User.objects.get_or_create(email='albert@example.com', password='Donkey99')
        cls.user2, _ = User.objects.get_or_create(email='ralph@example.com', password='Donkey77')
        create_leagues()
        create_teams()
        create_watchers(cls.user1)
        create_watchers(cls.user2)


class TeamAPITests(BaseAPITests):

    def test_team_list_view(self):
        url = reverse('team-list')
        resp_json = self.client.get(url).json()
        self.assertEqual(
            [item['name'] for item in resp_json],
            ['Huffies', 'Jerk Shoes', 'Dog Balls', 'Taco Trucks']
        )

    def test_team_detail_view(self):
        team_id = Team.objects.first().id
        url = reverse('team-detail', args=[team_id])
        resp_json = self.client.get(url).json()
        self.assertEqual(
            resp_json['name'],
            'Huffies'
        )

    def test_team_list_read_only(self):
        url = reverse('team-list')
        payload = {"notification_method": "email", "notify_away_games": True, "hours_before": 2, "team_id": 1} 
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 401)
        self.client.force_authenticate(user=self.user1)
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 403)
        resp = self.client.put(url, payload)
        self.assertEqual(resp.status_code, 403)
        resp = self.client.patch(url, payload)
        self.assertEqual(resp.status_code, 403)
        resp = self.client.delete(url, payload)
        self.assertEqual(resp.status_code, 403)

    def test_team_detail_read_only(self):
        team_id = Team.objects.first().id
        url = reverse('team-detail', args=[team_id])
        payload = {"notification_method": "email", "notify_away_games": True, "hours_before": 2, "team_id": 1} 
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 401)
        self.client.force_authenticate(user=self.user1)
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 403)
        resp = self.client.put(url, payload)
        self.assertEqual(resp.status_code, 403)
        resp = self.client.patch(url, payload)
        self.assertEqual(resp.status_code, 403)
        resp = self.client.delete(url, payload)
        self.assertEqual(resp.status_code, 403)


class UserAPITests(BaseAPITests):

    def create_superuser(self):
        User.objects.create_superuser(email='gorf@example.com', password="CheeseWheel")
        superuser = User.objects.get(email='gorf@example.com')
        self.assertEqual(superuser.is_superuser, True)

    def test_user_validated_phone(self):
        user_id = self.user1.id
        self.assertEqual(self.user1.phone_number, '')
        self.assertEqual(self.user1.has_validated_phone, False)
        self.user1.has_validated_phone = True
        self.user1.save()
        saved_user = User.objects.get(id=user_id)
        self.assertEqual(saved_user.has_validated_phone, False)
        self.user1.phone_number = 'notanumber'
        self.user1.save()
        saved_user = User.objects.get(id=user_id)
        self.assertEqual(saved_user.phone_number, '')
        self.user1.phone_number = '5556789876'
        self.user1.save()
        self.user1.has_validated_phone = True
        self.user1.save()
        saved_user = User.objects.get(id=user_id)
        self.assertEqual(saved_user.has_validated_phone, True)

    #def test_validate_phone_view(self):
    #    thing = AuthyApiClient()
    #    thing.
    #    url = '/accounts/phone_validate/'
    #    self.client.force_authenticate(user=self.user1)
    #    resp = self.client.get(url)
    #    self.assertEqual(resp.status_code, 200)
    #    #import pdb; pdb.set_trace()

    def test_fields_required(self):
        outbox = mail.outbox
        self.assertEqual(len(outbox), 0)
        url = '/rest-auth/registration/'
        payload = {"email": "", "password1": "", "password2": "", "time_zone": "", "phone_number": ""} 
        expected_resp_json = {'password1': ['This field may not be blank.'],
                              'email': ['This field may not be blank.'],
                              'time_zone': ['This field may not be blank.'],
                              'password2': ['This field may not be blank.']}
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), expected_resp_json)
        payload = {"email": "", "password1": "", "password2": "", "time_zone": "", "phone_number": ""} 

    def test_email_taken(self):
        url = '/rest-auth/registration/'
        payload = {"email": "albert@example.com", "password1": "ILoveTacos", "password2": "ILoveTacos", "time_zone": "US/Eastern", "phone_number": "5556798786"} 
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['email'][0], 'A user is already registered with this e-mail address.')

    def test_full_user_registration_process(self):
        outbox = mail.outbox
        self.assertEqual(len(outbox), 0)
        url = '/rest-auth/registration/'
        payload = {"email": "chewy@example.com", "password1": "ILoveTacos", "password2": "ILoveTacos", "time_zone": "US/Eastern", "phone_number": "5556798786"} 
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(outbox), 1)
        conf_email = outbox[0]
        self.assertEqual(conf_email.to[0], 'chewy@example.com')
        self.assertEqual(conf_email.subject, '[example.com] Activate your Sports Warning Account')
        url = '/rest-auth/login/'
        payload = {"email": "chewy@example.com", "password": "ILoveTacos"}
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['non_field_errors'][0], 'E-mail is not verified.')
        email = EmailAddress.objects.get(email='chewy@example.com')
        key = EmailConfirmationHMAC(email).key
        url = '/rest-auth/registration/verify-email/'
        payload = {"key": key}
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 200)
        url = '/rest-auth/login/'
        payload = {"email": "chewy@example.com", "password": "ILoveTacos"}
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 200)


class WatcherAPITests(BaseAPITests):

    def test_unauth_watcher_list_get_fails(self):
        url = reverse('watch-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 401)

    def test_watcher_list_get(self):
        url = reverse('watch-list')
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_watcher_create(self):
        url = reverse('watch-create')
        team_id = Team.objects.first().id
        self.client.force_authenticate(user=self.user1)
        payload = {"notification_method": "email", "notify_away_games": True, "hours_before": 2, "team_id": team_id} 
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 201)

    def test_watcher_create_fails(self):
        url = reverse('watch-create')
        self.client.force_authenticate(user=self.user1)
        payload = {"notification_method": "email", "notify_away_games": True, "hours_before": 2} 
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 400)

    def test_watcher_team_does_not_exist(self):
        url = reverse('watch-create')
        self.client.force_authenticate(user=self.user1)
        payload = {"notification_method": "email", "notify_away_games": True, "hours_before": 2, "team_id": 9999} 
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 400)

    def test_watcher_cannot_create_sms_without_valid_phone(self):
        watcher = Watcher.objects.filter(user=self.user1).first()
        watcher_id = watcher.id
        url = reverse('watch-detail', args=[watcher_id])
        self.client.force_authenticate(user=self.user1)
        payload = {"id": watcher.id, "notification_method": "both", "notify_away_games": True, "hours_before": 2, "team_id": watcher.team.id} 
        resp = self.client.put(url, payload)
        self.assertEqual(resp.status_code, 200)
        saved_watcher = Watcher.objects.get(id=watcher_id)
        self.assertEqual(saved_watcher.notification_method, "email")

    def test_watcher_update(self):
        watcher = Watcher.objects.filter(user=self.user1).first()
        url = reverse('watch-detail', args=[watcher.id])
        self.client.force_authenticate(user=self.user1)
        payload = {"id": watcher.id, "notification_method": "email", "notify_away_games": False, "hours_before": watcher.hours_before + 2, "team_id": watcher.team.id} 
        resp = self.client.put(url, payload)
        self.assertEqual(resp.status_code, 200)

    def test_watcher_team_change_fails(self):
        watcher = Watcher.objects.filter(user=self.user1).first()
        watcher_id = watcher.id
        old_team = watcher.team
        new_team_id = watcher.team.id + 1
        url = reverse('watch-detail', args=[watcher_id])
        self.client.force_authenticate(user=self.user1)
        payload = {"id": watcher_id, "notification_method": "email", "notify_away_games": True, "hours_before": watcher.hours_before, "team_id": new_team_id} 
        resp = self.client.put(url, payload)
        self.assertEqual(resp.status_code, 200)
        watcher = Watcher.objects.get(id=watcher_id)
        self.assertEqual(old_team, watcher.team)

    def test_watcher_user_change_fails(self):
        watcher = Watcher.objects.filter(user=self.user1).first()
        watcher_id = watcher.id
        new_user_id = self.user2.id
        url = reverse('watch-detail', args=[watcher_id])
        self.client.force_authenticate(user=self.user1)
        payload = {"id": watcher_id, "notification_method": "email", "notify_away_games": True, "hours_before": watcher.hours_before, "team_id": watcher.team.id, "user_id": new_user_id} 
        resp = self.client.put(url, payload)
        self.assertEqual(resp.status_code, 200)
        watcher = Watcher.objects.get(id=watcher_id)
        self.assertEqual(self.user1, watcher.user)

    def test_watcher_method_not_allowed(self):
        watcher = Watcher.objects.filter(user=self.user1).first()
        url = reverse('watch-detail', args=[watcher.id])
        self.client.force_authenticate(user=self.user1)
        payload = {"id": watcher.id, "notification_method": "email", "notify_away_games": False, "hours_before": watcher.hours_before + 2, "team_id": watcher.team.id} 
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 405)

    def test_watcher_update_unauthorized(self):
        watcher = Watcher.objects.filter(user=self.user1).first()
        url = reverse('watch-detail', args=[watcher.id])
        self.client.force_authenticate(user=self.user2)
        payload = {"id": watcher.id, "notification_method": "email", "notify_away_games": False, "hours_before": watcher.hours_before + 2, "team_id": watcher.team.id} 
        resp = self.client.put(url, payload)
        self.assertEqual(resp.status_code, 403)


class EventsAlertsTestCase(TestCase):

    def setUp(self):
        create_leagues()
        create_teams()
        self.team1 = Team.objects.first()
        self.user1, _ = User.objects.get_or_create(email='randy@example.com', password='ShoesAreFun')
        self.scheduler = Scheduler.objects.create()

    def test_create_event(self):
        event_time = timezone.now() + timezone.timedelta(hours=2)
        event, _ = Event.objects.get_or_create(opponent='carl malone', game_datetime=event_time, home=True, team=self.team1)
        event_details = {'gametime': event_time, 'location': 'home', 'team_name': 'Huffies'}
        self.assertEqual(event.get_details(), event_details)
        self.assertEqual(event.opponent, 'carl malone')

    def test_create_event_fails(self):
        event_time = timezone.now() + timezone.timedelta(hours=2)
        with self.assertRaises(IntegrityError):
            Event.objects.create(game_datetime=event_time, home=True, seatgeek_id=5, opponent='cheese dog')

    def test_event_has_passed(self):
        event_time = timezone.now() - timezone.timedelta(days=2)
        event, _ = Event.objects.get_or_create(opponent='hot wallace', game_datetime=event_time, home=True, team=self.team1)
        self.assertEqual(event.has_passed(), True)

    def test_watcher_creates_alert(self):
        event_time = timezone.now() + timezone.timedelta(hours=2)
        event, _ = Event.objects.get_or_create(opponent='carl malone', game_datetime=event_time, home=True, team=self.team1)
        watcher, _ = Watcher.objects.get_or_create(team=self.team1, user=self.user1, hours_before=2, notification_method='email', notify_away_games=False)
        prev_alerts = Alert.objects.filter(watcher=watcher)
        self.assertEqual(len(prev_alerts), 0)
        self.scheduler.create_alerts(2)
        curr_alerts = Alert.objects.filter(watcher=watcher)
        self.assertEqual(len(curr_alerts), 1)

    def test_watcher_does_not_create_away_alert(self):
        event_time = timezone.now() + timezone.timedelta(hours=4)
        event, _ = Event.objects.get_or_create(opponent='carl malone', game_datetime=event_time, home=False, team=self.team1)
        watcher, _ = Watcher.objects.get_or_create(team=self.team1, user=self.user1, hours_before=1, notification_method='email', notify_away_games=False)
        prev_alerts = Alert.objects.filter(watcher=watcher)
        self.assertEqual(len(prev_alerts), 0)
        self.scheduler.create_alerts(4)
        curr_alerts = Alert.objects.filter(watcher=watcher)
        self.assertEqual(len(curr_alerts), 0)

    def test_create_duplicate_event_fails(self):
        event_time = timezone.now() + timezone.timedelta(hours=2)
        Event.objects.create(team=self.team1, game_datetime=event_time, seatgeek_id=5, home=True)
        with self.assertRaises(IntegrityError):
            Event.objects.create(team=self.team1, game_datetime=event_time, seatgeek_id=5, home=True)
"""
    ### watchers
        cannot set notif to sms or both without validated phone
    #def test_cannot_send_sms_without_validated_phone(self):

    ### users
        registration
        validation 
        logging in / out
        updating all settings
        validating phone
        token auth

    ### alerts
        sms will not send without validated phone
        alerts send on time
        alerts respect timezone
        alert content
        alert recipient
        alert email
        alert sms
        alert both

    ### webtests
        selenium
"""

