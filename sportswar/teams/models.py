from django.db import models


class League(models.Model):

    def __str__(self):
        return 'League - {}'.format(self.name)

    name = models.CharField(max_length=10, unique=True)


class Team(models.Model):

    class Meta:
        unique_together = (('name', 'league',))

    def __str__(self):
        return ' - '.join([self.league.name, self.name, self.slug])

    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
