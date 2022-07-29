from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from pyot.utils.lol.routing import platform_to_region
from asgiref.sync import sync_to_async
from tracker.utils.constants import regionChoices, platformChoices, tierChoices, rankChoices
# Choices for ease of use on choice fields. Could be stored in constants.py, but isn't done since usage is constrained to this file for now.

class User(AbstractUser): # Override user model for future use, just in case. See: https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
    pass 

class Player(models.Model):
    name = models.CharField(max_length=24)
    avatar_id = models.CharField(max_length=24, default="")
    puuid = models.CharField(max_length=100, default="")
    summoner_id = models.CharField(max_length=100, default="")
    account_id = models.CharField(max_length=100, default="")
    region = models.CharField(max_length=10, default='europes', choices=regionChoices)
    platform = models.CharField(max_length=10, default='euw1', choices=platformChoices)
    last_data_update = models.DateTimeField(default=timezone.now)
    # Ranked data
    tier = models.CharField(max_length=100, default='UNRANKED', choices=tierChoices)
    rank = models.CharField(max_length=5, default='NONE', choices=rankChoices)
    lp = models.IntegerField(default=0, verbose_name='LP')
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    winrate = models.FloatField(default=0)
    streak = models.IntegerField(default=0)
    last_ranked_update = models.DateTimeField(default=timezone.now) # mostly for debugging

    @classmethod
    def create(cls, name, platform, avatar_id=""):
        res = cls(name=name, platform=platform, region=platform_to_region(platform), avatar_id=avatar_id)
        return res
    def __str__(self): # For admin panel aesthetics
        return self.name
#TODO: Implement django-model-history so I can get stadistics out of this model.

class Challenge(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_absolute = models.BooleanField()
    last_access_date = models.DateTimeField(default=timezone.now) # Debugging
    ignore_unranked = models.BooleanField(default=True)


class Challenge_Player(models.Model):
    # Foreign keys to relate a challenge and a player 
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    challenge_id = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    # Starting state and settings.
    starting_rank = models.CharField(max_length=20, choices=rankChoices) 
    starting_tier = models.CharField(max_length=30, choices=tierChoices) # Doesn't use ChoiceField for now since this has to be updated programmatically.
    starting_lp = models.IntegerField()
    ignored = models.BooleanField(default=False)
    # Current state of the player
    progress = models.IntegerField(default=0)
    progress_delta = models.IntegerField(default=0)
    last_update = models.DateTimeField(default=timezone.now)
    def __str__(self): # For admin panel aesthetics
        return "{0}-{1}".format(self.challenge_id.id, self.player_id.name)
    class Meta:
        indexes = [
            models.Index(fields=['player_id', 'challenge_id'])
        ]
