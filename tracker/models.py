from django.db import models
from django.utils import timezone
# Create your models here.

#TODO: Implement django-model-history so I can get stadistics out of this model.
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
    streak = models.CharField(max_length=5, default='EEEEE') #TODO: Implement this



# TODO: Add ChallengeList to either this or LeagueData so we can have multiple leaderboards. For now, Challenge is a glorified way to store a date.
# Using Junction tables to store lists: https://stackoverflow.com/a/444268
class TrackedPlayers(models.Model):
    regionChoices = [('EUW', 'EUW1'),
                     ("BR","BR1"),
                     ("EUNE", "EUN1"),
                     ('JP', 'JP1'),
                     ('KR', 'KR1'),
                     ('LAN', 'LA1'),
                     ('LAS', 'LA2'),
                     ('OCE', 'OC1'),
                     ('RU', 'RU'),
                     ('TR', 'TR1')]
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
    #Defaults set just to prevent ------ from showing up in choices.
    startingTier = models.CharField(max_length=30, choices=tierChoices, default='SILVER')
    startingRank = models.CharField(max_length=10, choices=rankChoices, default='I')
    startingPoints = models.IntegerField()
    region = models.CharField(max_length=10, choices=regionChoices, default='EUW')
    ignored = models.BooleanField(default=False)

class Challenge(models.Model):
    queueTypeChoices = [('SoloQ', 'RANKED_SOLO_5x5'),
                 ('Flex', 'RANKED_FLEX_5x5')]
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    endDate = models.DateField()
    queueType = models.CharField(max_length=25, choices=queueTypeChoices, default='RANKED_SOLO_5x5')
    lastUpdate = models.DateTimeField(default=timezone.now)
