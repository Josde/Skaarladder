import os
import traceback

import riotwatcher
from django.core.exceptions import *

from . import constants
from .models import LeagueData


def rankToLP(rank, tier, points):
    return (constants.rankWeights[rank]) * 400 + (constants.tierWeights[tier]) * 100 + int(points)


def updatePlayerData(playerName, region, queueType, startingTier, startingRank, startingPoints):
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    try:
        summonerData = lolWatcher.summoner.by_name(region, playerName)
        allLeagueData = lolWatcher.league.by_summoner(region, summonerData['id'])
        for element in allLeagueData:
            if element['queueType'] == queueType:
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
                    player.progressDelta = player.progress - player.progressDelta
                    print("[LeagueData] Successfully updated existing player", playerName)
                    player.save()
                except ObjectDoesNotExist:
                    player = LeagueData.objects.create(name=summonerData['name'], tier=leagueData['tier'],
                                                       rank=leagueData['rank'],
                                                       points=leagueData['leaguePoints'], wins=leagueData['wins'],
                                                       losses=leagueData['losses'], winrate=winrate,
                                                       progress=currentLP-startingLP, progressDelta=0)
                    print("[LeagueData] Successfully created non-existing player", playerName)
                    player.save()

    except Exception as ex:
        print("Exception {0} ocurred while looking up player {1}".format(type(ex).__name__, playerName))
        traceback.print_exc()
