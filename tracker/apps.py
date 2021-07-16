from django.apps import AppConfig
import os
from django.core.exceptions import ObjectDoesNotExist

from tracker.exceptions import StartingRankException


class TrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'

    def ready(self):
        regions = os.environ.get("REGION", default="")
        playernames = os.environ.get("PLAYERS", default="")
        startingRanks = os.environ.get("STARTING_RANKS", default="")

        if (len(playernames) == 0 or len(startingRanks) == 0):
            print("[Startup] No players / starting ranks detected in environment variables. Skipping initial setup.")
            print("If you haven't added your players yet, you can still do so by setting environment variables and restarting.")
            print("Or alternatively through Django control panel.")
            return
        else:
            # If they are not blank, interpret as list.
            playernames = os.environ.get("PLAYERS").split(",")
            startingRanks = os.environ.get("STARTING_RANKS").split(",")
        if len(playernames) != len(startingRanks):
            print("[Startup] Player names ({0}) and starting ranks ({1}) don't match up, skipping initial setup.".format(len(playernames), len(startingRanks)))
            print("If you haven't added your players yet, you can still do so by setting environment variables and restarting.")
            print("Or alternatively through Django control panel.")
            return
        if len(regions) == 0:
            # If blank, set default.
            print("[Startup] No region detected, set default to EUW1")
            regions = ["euw1"] * len(playernames)
        else:
            # If not blank, interpret as list.
            regions = os.environ.get("REGION").split(",")
        if len(regions) == 1:
            # If its a one-element list, interpret as default for all users.
            print("[Startup] Region is only one entry, interpreting as default for all users.")
            regions = regions * len(playernames)

        from tracker.models import TrackedPlayers
        # populate TrackerPlayers model
        # This will be skipped if PLAYERS / STARTING_RANKS are not set or incorrect.
        for playerName, startingRank, region in zip(playernames, startingRanks, regions):
            try:
                # if player exists, we dont't have to do anything
                player = TrackedPlayers.objects.get(name=playerName)
                print("Player {0} already in tracked players, skipping.".format(playerName))
                continue
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

