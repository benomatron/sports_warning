from rest_framework import serializers

from sportswar.teams.models import Team


class TeamSerializer(serializers.ModelSerializer):
    league_id = serializers.ReadOnlyField()

    class Meta:
        model = Team
        fields = ('id', 'league_id', 'name', 'slug')
