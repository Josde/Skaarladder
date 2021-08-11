from django.apps import AppConfig
import os
from django.core.exceptions import ObjectDoesNotExist
import datetime
from tracker.exceptions import StartingRankException
import sys



class TrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'

    def ready(self):
        print("%n%n%n%n----------------------------")
        print("ARGUMENTS: {0}", sys.argv)
        print("----------------------------%n%n%n%n")
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv: #dont run this on migrations
            SKIP_TRACKEDPLAYERS = False
            SKIP_CHALLENGE = False
            USE_ENVDATES = True
            regions = os.environ.get("REGION", default="")
            playernames = os.environ.get("PLAYERS", default="")
            startingRanks = os.environ.get("STARTING_RANKS", default="")
            ignoredPlayers = os.environ.get("IGNORED_PLAYERS", default="")

            if len(ignoredPlayers) != 0:
                ignoredPlayers = os.environ.get("IGNORED_PLAYERS").split(",")
                print("[Startup] Found ignored players" , ignoredPlayers)
            if len(playernames) == 0 or len(startingRanks) == 0:
                print("[Startup] No players / starting ranks detected in environment variables. Skipping initial setup.")
                print("If you haven't added your players yet, you can still do so by setting environment variables and restarting.")
                print("Or alternatively through Django control panel.")
                SKIP_TRACKEDPLAYERS = True
            else:
                # If they are not blank, interpret as list.
                playernames = os.environ.get("PLAYERS").split(",")
                startingRanks = os.environ.get("STARTING_RANKS").split(",")
            if len(playernames) != len(startingRanks):
                print("[Startup] Player names ({0}) and starting ranks ({1}) don't match up, skipping initial setup.".format(len(playernames), len(startingRanks)))
                print("If you haven't added your players yet, you can still do so by setting environment variables and restarting.")
                print("Or alternatively through Django control panel.")
                SKIP_TRACKEDPLAYERS = True

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
            if not SKIP_TRACKEDPLAYERS:
                from tracker.models import TrackedPlayers
                from .misc import getPuuid
                # populate TrackerPlayers model
                # This will be skipped if PLAYERS / STARTING_RANKS are not set or incorrect.
                for playerName, startingRank, region in zip(playernames, startingRanks, regions):
                    try:
                        # if player exists, we dont't have to do anything
                        player = TrackedPlayers.objects.get(name=playerName)
                        if player.puuid == "":
                            player.puuid = getPuuid(player.name, player.region)
                            print("[Startup] Added missing PUUID {0} for existing player {1}".format(player.puuid, player.name))
                            player.save()
                        print("Player {0} already in tracked players, skipping.".format(playerName))
                        continue
                    except ObjectDoesNotExist:
                        # if player does not exist, get data from API.
                        try:
                            startingRankSplit = startingRank.split(" ")
                            if len(startingRankSplit) != 3:
                                raise StartingRankException
                        except StartingRankException:
                            print("Malformed starting rank for player {0}, skipping...".format(playerName))
                            continue
                        isIgnored = True if playerName in ignoredPlayers else False
                        puuid = getPuuid(playerName, region)
                        player = TrackedPlayers.objects.create(name=playerName, puuid=puuid, startingTier=startingRankSplit[0],
                                                               startingRank=startingRankSplit[1],
                                                               startingPoints=startingRankSplit[2],
                                                               region=region, ignored=isIgnored)
                        print("[TrackedPlayers] Successfully created non-existing player", playerName)
                        player.save()
            from .models import Challenge
            if len(Challenge.objects.all()) != 0:
                print("[Challenge] A challenge is already configured. Skipping setup.")
                SKIP_CHALLENGE = True
            else:
                print("[Challenge] A challenge is not configured yet.")
                endDay = os.getenv("ENDDATE_DAY", default="")
                endMonth = os.getenv("ENDDATE_MONTH", default="")
                endYear = os.getenv("ENDDATE_YEAR", default="")
                if endDay == "" or endMonth == "" or endYear == "":
                    print("[Challenge] No ENDDATE_ environment variables set. Will setup challenge end in a month.")
                    USE_ENVDATES = False
                else:
                    try:
                        enddate = datetime.datetime(int(endYear), int(endMonth), int(endDay))
                        if not (enddate < datetime.datetime.today()):
                            print("[Challenge] Valid date found in environment variables. Setting up Challenge end to '{0}'".format(enddate))
                            USE_ENVDATES = True
                        else:
                            print("[Challenge] Found valid date in environment variables, but it has already passed. Set challenge end in a month.")
                            USE_ENVDATES = False
                    except ValueError:
                        print("[Challenge] Invalid date '{0}-{1}-{2}' found in environment variables. Will setup challenge end in a month.".format(endDay, endMonth, endYear))
                        USE_ENVDATES = False
            if not SKIP_CHALLENGE:
                if USE_ENVDATES:
                    endDay = os.getenv("ENDDATE_DAY")
                    endMonth = os.getenv("ENDDATE_MONTH")
                    endYear = os.getenv("ENDDATE_YEAR")
                    challenge = Challenge.objects.create(pk=1, name="SOLOQ CHALLENGE", endDate=datetime.date(year=int(endYear), month=int(endMonth), day=int(endDay)))
                    print("[Challenge] Successfully created challenge {0}. Ends {1}.".format("SOLOQ CHALLENGE", datetime.date(year=int(endYear), month=int(endMonth), day=int(endDay))))
                else:
                    endDate = datetime.date.today() + datetime.timedelta(days=+31)
                    challenge = Challenge.objects.create(pk=1, name="SOLOQ CHALLENGE", endDate=endDate)
                    print("[Challenge] Successfully created challenge {0}. Ends {1}.".format("SOLOQ CHALLENGE", endDate))
                challenge.save()