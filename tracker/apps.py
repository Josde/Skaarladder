from django.apps import AppConfig
import os
from django.core.exceptions import ObjectDoesNotExist

from tracker.exceptions import StartingRankException


class TrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'

    def ready(self):
        from tracker.models import TrackedPlayers
        # populate TrackerPlayers model
        # TODO: Improve "REGION" usability by making it a list.
        region = os.environ.get("REGION", default="euw1")
        playernames = os.environ.get("PLAYERS").split(",")
        startingRanks = os.environ.get("STARTING_RANKS").split(",")
        queueType = os.environ.get("QUEUE_TYPE", default="RANKED_SOLO_5x5")
        for playerName, startingRank in zip(playernames, startingRanks):
            try:
                # if player exists, we dont't have to do anything
                player = TrackedPlayers.objects.get(name=playerName)
                print("Player {0} already in tracked players, skipping.".format(playerName))
            except ObjectDoesNotExist:
                # if player does not exist, parse it from .env
                try:
                    startingRankSplit = startingRank.split(" ")
                    if (len(startingRankSplit) != 3):
                        raise StartingRankException
                except StartingRankException:
                    print("Malformed starting rank for player {0}, skipping...".format(playerName))
                    continue
                player = TrackedPlayers.objects.create(name=playerName, startingTier=startingRankSplit[0],
                                                       startingRank=startingRankSplit[1],
                                                       startingPoints=startingRankSplit[2],
                                                       region=region)
                print("[TrackedPlayers] Successfully created non-existing player", playerName)
                player.save()

