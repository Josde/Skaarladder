from django.db import models

# Create your models here.
class LeagueData(models.Model):
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=100)
    rank = models.CharField(max_length=100)
    points = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    winrate = models.FloatField()
    progress = models.IntegerField()

