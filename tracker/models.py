from django.db import models
from django.utils import timezone
# Create your models here.

#TODO: Implement django-model-history so I can get stadistics out of this model.
class LeagueData(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    puuid = models.CharField(max_length=100, default="")
    tier = models.CharField(max_length=100, default='IRON')
    rank = models.CharField(max_length=100, default='IV')
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    winrate = models.FloatField(default=0)
    progress = models.IntegerField(default=0)
    progressDelta = models.IntegerField(default=0)
    streak = models.CharField(max_length=5, default='EEEEE')



# TODO: Add ChallengeList to either this or LeagueData so we can have multiple leaderboards. For now, Challenge is a glorified way to store a date.
# Using Junction tables to store lists: https://stackoverflow.com/a/444268
class TrackedPlayers(models.Model):
    regionChoices = [('EUW1', 'EUW1'),
                     ("BR1","BR1"),
                     ("EUN1", "EUN1"),
                     ('JP1', 'JP1'),
                     ('KR1', 'KR1'),
                     ('LA1', 'LA1'),
                     ('LA2', 'LA2'),
                     ('OC1', 'OC1'),
                     ('RU', 'RU'),
                     ('TR1', 'TR1')]
    tierChoices = [('IRON', 'IRON'),
                   ('BRONZE', 'BRONZE'),
                   ('SILVER', 'SILVER'),
                   ('GOLD', 'GOLD'),
                   ('PLATINUM', 'PLATINUM'),
                   ('DIAMOND', 'DIAMOND')]
    rankChoices = [('I', 'I'),
                   ('II', 'II'),
                   ('III', 'III'),
                   ('IV', 'IV')]
    name = models.CharField(max_length=100, primary_key=True)
    id = models.CharField(max_length=100, default="")
    accountId = models.CharField(max_length=100, default="")
    puuid = models.CharField(max_length=100, default="")
    #Defaults set just to prevent ------ from showing up in choices.
    startingTier = models.CharField(max_length=30, choices=tierChoices, default='SILVER')
    startingRank = models.CharField(max_length=10, choices=rankChoices, default='I')
    startingPoints = models.IntegerField()
    region = models.CharField(max_length=10, choices=regionChoices, default='EUW')
    ignored = models.BooleanField(default=False)

class Challenge(models.Model):
    queueTypeChoices = [('RANKED_SOLO_5x5', 'RANKED_SOLO_5x5'),
                 ('RANKED_FLEX_SR', 'RANKED_SR_5x5')]
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    endDate = models.DateField()
    queueType = models.CharField(max_length=25, choices=queueTypeChoices, default='RANKED_SOLO_5x5')
    lastUpdate = models.DateTimeField(default=timezone.now)
