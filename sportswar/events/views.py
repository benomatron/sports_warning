from django.views import generic

from sportswar.teams.models import Team


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'sportswarning_index'

    def get_queryset(self):
        return Team.objects.all().order_by('id')
