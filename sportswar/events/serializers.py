from rest_framework import serializers
from sportswar.events.models import Alert, Event, Watcher
from sportswar.teams.serializers import TeamSerializer


class EventSerializer(serializers.ModelSerializer):
    team = TeamSerializer(many=False, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'opponent', 'game_datetime', 'home', 'team')


class WatcherSerializer(serializers.ModelSerializer):
    team_id = serializers.ReadOnlyField()
    user_id = serializers.ReadOnlyField()

    class Meta:
        model = Watcher
        fields = ('id', 'team_id', 'user_id', 'hours_before',
                  'notification_method', 'notify_away_games')


class AlertSerializer(serializers.ModelSerializer):
    watcher_id = serializers.ReadOnlyField()

    class Meta:
        model = Alert
        fields = ('id', 'watcher_id', 'alert_time')
