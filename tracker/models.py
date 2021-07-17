from django.db import models


# Create your models here.


class LeagueData(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    tier = models.CharField(max_length=100)
    rank = models.CharField(max_length=100)
    points = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    winrate = models.FloatField()
    progress = models.IntegerField()
    progressDelta = models.IntegerField()


# TODO: Add ChallengeList to either this or LeagueData so we can have multiple leaderboards. For now, Challenge is a glorified way to store a date.
# Using Junction tables to store lists: https://stackoverflow.com/a/444268
class TrackedPlayers(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    startingTier = models.CharField(max_length=30)
    startingRank = models.CharField(max_length=10)
    startingPoints = models.IntegerField()
    region = models.CharField(max_length=10)


class Challenge(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    endDate = models.DateField()
    # queueType = models.CharField(max_length=25) for some reason this is triggering django problems, commented temporarily
