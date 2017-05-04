import logging
import requests

from django.db import IntegrityError
from django.conf import settings
from django.utils import timezone

from sportswar.teams.models import League, Team
from sportswar.events.models import Event
from sportswar.utils.teamlist import ALL_TEAMS


logger = logging.getLogger(__name__)

EVENTS_URL = 'https://api.seatgeek.com/2/events?&performers.slug='

LEAGUES = [
    'mlb',
    'nba',
    'nfl',
    'nhl'
]

MAX_PAGES = 100


def init_db():
    for league in LEAGUES:
        try:
            League.objects.create(name=league)
            print('Created league: {}'.format(league))
        except IntegrityError:
            print('Skipping {}: May already exist'.format(league))

    for team in ALL_TEAMS:
        try:
            league = League.objects.get(name=team[2])
            Team.objects.create(name=team[0], slug=team[1], league=league)
        except IntegrityError:
            print('Skipping {}: May already exist'.format(team))


def get_events_for_team(team_slug, ret_events, page_num=1, start_date=None, end_date=None):

    page_num = 1 if page_num < 1 else page_num
    if page_num > MAX_PAGES:
        logger.warning('page_num > 100 for team: %s', team_slug)
        return ret_events

    url = EVENTS_URL + team_slug
    if start_date and end_date:
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        url += '&datetime_utc.gte={start}&datetime_utc.lte={end}'.format(start=start_date, end=end_date)
    if page_num > 1:
        url += '&page={}'.format(page_num)
    url += '&per_page=100'

    res = requests.get(url, auth=(settings.SEATGEEK_CLIENT_ID, settings.SEATGEEK_SECRET))

    if res.status_code == 200:
        res_json = res.json()
        meta = res_json['meta']
        events = res_json['events']
        page = meta.get('page', 1) or 1
        per_page = meta.get('per_page', 1) or 1
        total = meta.get('total', 1) or 1

        if page != page_num:
            raise IntegrityError('Page of seatgeek request is out of sync!')
        if (page * per_page) < total:
            ret_events += get_events_for_team(team_slug, events, page_num+1, start_date, end_date)
        else:
            ret_events += events
    else:
        res.raise_for_status()

    return ret_events


def create_events_from_schedule(team, start_date=None, end_date=None):

    events = get_events_for_team(team.slug, [], 1, start_date, end_date)

    for event in events:
        gametime = event['datetime_utc']
        gametime += '+00:00'  # TODO: This is a shoddy way to add timezone
        performers = event['performers']
        seatgeek_id = event['id']
        home = False
        opponent = None
        for perf in performers:
            if perf['slug'] == team.slug:
                if perf.get('home_team', False):
                    home = True
            else:
                opponent = perf['name']
        try:
            event = Event.objects.create(team=team, game_datetime=gametime, home=home,
                                         opponent=opponent, seatgeek_id=seatgeek_id)
            logger.info('Created event: %s', event)
        except IntegrityError:
            pass


def create_events_for_all_teams():
    teams = Team.objects.all()
    start_date = timezone.now() - timezone.timedelta(days=1)
    end_date = start_date + timezone.timedelta(days=7)
    for team in teams:
        create_events_from_schedule(team, start_date, end_date)
