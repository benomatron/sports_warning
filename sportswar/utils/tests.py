from unittest.mock import patch

from django.utils import timezone
from django.test import TestCase

from sportswar.events.models import Event
from sportswar.teams.models import Team, League
from sportswar.utils.build_db import create_events_from_schedule, init_db


EXAMPLE_EVENT_JSON = {'events': [{'announce_date': '2016-08-12T00:00:00', 'visible_until_utc': '2017-01-05T04:30:00',
                      'stats': {'lowest_price': 133.0, 'highest_price': 5426.0, 'listing_count': 616, 'lowest_price_good_deals': 133.0, 'average_price': 301.0},
                      'type': 'nba', 'performers': [{'slug': 'new-york-knicks',
                      'image': 'https://chairnerd.global.ssl.fastly.net/images/performers-landscape/new-york-knicks-bcf9eb/2090/huge.jpg',
                      'name': 'New York Knicks', 'primary': True,
                      'images': {'huge': 'https://chairnerd.global.ssl.fastly.net/images/performers-landscape/new-york-knicks-bcf9eb/2090/huge.jpg'},
                      'stats': {'event_count': 48}, 'home_venue_id': 93, 'divisions': [{'slug': None, 'taxonomy_id': 1030100, 'short_name': None, 'display_type': 'Conference', 'division_level': 1,
                      'display_name': 'Eastern Conference'}, {'slug': 'eastern-atlantic', 'taxonomy_id': 1030100, 'short_name': 'Atlantic', 'display_type': 'Division', 'division_level': 2, 'display_name': 'Eastern - Atlantic'}],
                      'score': 0.803598, 'home_team': True, 'url': 'https://seatgeek.com/new-york-knicks-tickets', 'colors': {'all': ['#006BB6', '#F58426', '#BEC0C2', '#231F20'], 'primary': ['#006BB6', '#F58426'], 'iconic': '#006BB6'}, 'image_license': None, 'short_name': 'Knicks', 'has_upcoming_events': True, 'id': 2090, 'type': 'nba', 'taxonomies': [{'parent_id': None, 'name': 'sports', 'id': 1000000}, {'parent_id': 1000000, 'name': 'basketball', 'id': 1030000}, {'parent_id': 1030000, 'name': 'nba', 'id': 1030100}], 'image_attribution': "Provided by Stephen D'Amico"}, {'slug': 'milwaukee-bucks', 'image': 'https://chairnerd.global.ssl.fastly.net/images/performers-landscape/milwaukee-bucks-36e2b0/2097/huge.jpg', 'name': 'Milwaukee Bucks', 'images': {'huge': 'https://chairnerd.global.ssl.fastly.net/images/performers-landscape/milwaukee-bucks-36e2b0/2097/huge.jpg'}, 'stats': {'event_count': 49}, 'home_venue_id': 207, 'divisions': [{'slug': None, 'taxonomy_id': 1030100, 'short_name': None, 'display_type': 'Conference', 'division_level': 1, 'display_name': 'Eastern Conference'}, {'slug': 'eastern-central', 'taxonomy_id': 1030100, 'short_name': 'Central', 'display_type': 'Division', 'division_level': 2, 'display_name': 'Eastern - Central'}], 'image_attribution': 'https://www.flickr.com/photos/compujeramey/128264488', 'score': 0.635522, 'url': 'https://seatgeek.com/milwaukee-bucks-tickets', 'colors': {'all': ['#00471B', '#F0EBD2', '#061922', '#007DC5'], 'primary': ['#00471B', '#F0EBD2'], 'iconic': '#00471B'}, 'image_license': None, 'short_name': 'Bucks', 'has_upcoming_events': True, 'id': 2097, 'type': 'nba', 'taxonomies': [{'parent_id': None, 'name': 'sports', 'id': 1000000}, {'parent_id': 1000000, 'name': 'basketball', 'id': 1030000}, {'parent_id': 1030000, 'name': 'nba', 'id': 1030100}], 'away_team': True}], 'datetime_local': '2017-01-04T19:30:00', 'short_title': 'Bucks at Knicks', 'date_tbd': False, 'score': 0.753736, 'venue': {'slug': 'madison-square-garden', 'address': '4 Pennsylvania Plaza', 'timezone': 'America/New_York', 'city': 'New York', 'display_location': 'New York, NY', 'score': 0.898999, 'location': {'lat': 40.7509, 'lon': -73.9943}, 'url': 'https://seatgeek.com/venues/madison-square-garden/tickets', 'extended_address': 'New York, NY 10001', 'country': 'US', 'name': 'Madison Square Garden', 'links': [], 'id': 93, 'state': 'NY', 'postal_code': '10001'}, 'created_at': '2016-08-12T00:00:00', 'datetime_utc': '2017-01-05T00:30:00', 'url': 'https://seatgeek.com/bucks-at-knicks-tickets/1-4-2017-new-york-new-york-madison-square-garden/nba/3475252', 'title': 'Milwaukee Bucks at New York Knicks', 'time_tbd': False, 'datetime_tbd': False, 'links': [], 'id': 3475252, 'taxonomies': [{'parent_id': None, 'name': 'sports', 'id': 1000000}, {'parent_id': 1000000, 'name': 'basketball', 'id': 1030000}, {'parent_id': 1030000, 'name': 'nba', 'id': 1030100}]}],
                      'in_hand': {}, 'meta': {'per_page': 100, 'geolocation': None, 'took': 4, 'total': 1, 'page': 1}}


class UtilsTestCase(TestCase):

    def setUp(self):
        init_db()

    def test_leagues_and_teams(self):
        leagues = League.objects.all()
        teams = Team.objects.all()
        self.assertEqual(len(leagues), 4)
        self.assertEqual(len(teams), 122)

    def test_create_events_for_team(self):
        with patch('sportswar.utils.build_db.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = EXAMPLE_EVENT_JSON
            team = Team.objects.filter(league__name='nba').first()
            current_events = Event.objects.filter(team=team)
            self.assertEqual(len(current_events), 0)

            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(days=3)
            create_events_from_schedule(team, start_date, end_date)
            new_events = Event.objects.filter(team=team)
            self.assertEqual(len(new_events), 1)
