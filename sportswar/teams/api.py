from rest_framework import generics

from sportswar.permissions import IsReadOnly
from sportswar.teams.models import Team
from sportswar.teams.serializers import TeamSerializer


class TeamListView(generics.ListAPIView):
    permission_classes = (IsReadOnly,)

    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class TeamDetailView(generics.RetrieveAPIView):
    permission_classes = (IsReadOnly,)

    queryset = Team.objects.all()
    serializer_class = TeamSerializer
