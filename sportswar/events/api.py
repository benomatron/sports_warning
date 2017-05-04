import logging

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from sportswar.permissions import IsOwnerOrReadOnly
from sportswar.events.models import Watcher
from sportswar.events.serializers import WatcherSerializer
from sportswar.teams.models import Team


logger = logging.getLogger(__name__)


class WatcherListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrReadOnly,)

    serializer_class = WatcherSerializer

    def get_queryset(self):
        user = self.request.user
        return Watcher.objects.filter(user=user).order_by('-id')


class WatcherCreateView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = WatcherSerializer

    def create(self, request, *args, **kwargs):
        team_id = request.data.get('team_id', None)
        try:
            Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response('Team does not exist', status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = self.request.user
        team_id = self.request.data['team_id']
        team = Team.objects.get(id=team_id)
        serializer.save(user=user, team=team)


class WatcherDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrReadOnly,)

    serializer_class = WatcherSerializer

    def get_queryset(self):
        watcher_id = self.request.data.get('id', None)
        return Watcher.objects.filter(id=watcher_id)
