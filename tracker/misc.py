import riotwatcher
import os
from .exceptions import *
from .models import LeagueData
from django.core.exceptions import *
import traceback
def rankToLP(rank, tier, points):
    rankWeights = {
        "IRON" : 0,
        "BRONZE" : 1,
        "SILVER" : 2,
        "GOLD" : 3,
        "PLATINUM" : 4,
        "DIAMOND" : 5
    }
    tierWeights = {
        "IV" : 0,
        "III" : 1,
        "II" : 2,
        "I" : 3
    }
    return (rankWeights[rank]) * 400 + (tierWeights[tier]) * 100 + int(points)


def updatePlayerData(playerName, region, queueType, startingTier, startingRank, startingPoints):
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    ignoredPlayers = os.environ.get("IGNORED_PLAYERS").split(",")
    try:
        if (playerName in ignoredPlayers):  # skip players in ignored player list
            return
        summonerData = lolWatcher.summoner.by_name(region, playerName)
        allLeagueData = lolWatcher.league.by_summoner(region, summonerData['id'])
        for element in allLeagueData:
            if (element['queueType'] == queueType):
                leagueData = element
                winrate = float(leagueData['wins']) / (leagueData['wins'] + float(leagueData['losses']))
                startingLP = rankToLP(startingTier, startingRank, startingPoints)
                currentLP = rankToLP(leagueData['tier'], leagueData['rank'], leagueData['leaguePoints'])
                try:
                    player = LeagueData.objects.get(name=summonerData['name'])
                    player.tier = leagueData['tier']
                    player.rank = leagueData['rank']
                    player.points = leagueData['leaguePoints']
                    player.wins = leagueData['wins']
                    player.losses = leagueData['losses']
                    player.winrate = winrate
                    player.progress = currentLP - startingLP
                    print("[LeagueData] Successfully updated existing player", playerName)
                except ObjectDoesNotExist:
                    player = LeagueData.objects.create(name=summonerData['name'], tier=leagueData['tier'],
                                                       rank=leagueData['rank'],
                                                       points=leagueData['leaguePoints'], wins=leagueData['wins'],
                                                       losses=leagueData['losses'], winrate=winrate,
                                                       progress=currentLP - startingLP)
                    print("[LeagueData] Successfully created non-existing player", playerName)
                finally:
                    player.save()

    except Exception as ex:
        print("Exception {0} ocurred while looking up player {1}".format(type(ex).__name__, playerName))
        traceback.print_exc()