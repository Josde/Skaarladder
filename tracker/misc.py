import os
import traceback

import riotwatcher
from django.core.exceptions import *

from . import constants
from .models import LeagueData, TrackedPlayers


def rankToLP(rank, tier, points):
    return (constants.rankWeights[rank]) * 400 + (constants.tierWeights[tier]) * 100 + int(points)

def updateIds():
    for player in TrackedPlayers.objects.all():
        id, accountId, puuid = getIds(player.name, player.region)
        if (id == "" or accountId == "" or puuid == ""):
            return
        player.id = id
        player.accountId = accountId
        player.puuid = puuid
        print("[UpdateIds] New IDs for player {0}: {1} // {2} // {3}".format(player.name, id, accountId, puuid))
        player.save()

def getIds(playerName: str, region: str):
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    try:
        summonerData = lolWatcher.summoner.by_name(region, playerName)
        return summonerData['id'], summonerData['accountId'], summonerData['puuid']
    except Exception:
        return ["", "", ""]

#TODO: Refactor these to only take a primary key and do all the database logic too.
def updatePlayerData(playerName: str, puuid: str, accountId: str, id: str, region: str, queueType: int, startingTier: str, startingRank: str, startingPoints: int, oldProgress: int):
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    try:
        if len(accountId) < 20 or len(id) < 20 or len(puuid) < 20: #validity check, idk if theres a documented minimum
            summonerData = lolWatcher.summoner.by_name(region, playerName)
            validId = summonerData['id']
            validAccountId = summonerData['accountId']
            validPuuid = summonerData['puuid']
        else:
            validId = id
            validAccountId = accountId
            validPuuid = puuid
        allLeagueData = lolWatcher.league.by_summoner(region, validId)
        for element in allLeagueData:
            if element['queueType'] == queueType:
                leagueData = element
                winrate = float(leagueData['wins']) / (leagueData['wins'] + float(leagueData['losses']))
                startingLP = rankToLP(startingTier, startingRank, startingPoints)
                currentLP = rankToLP(leagueData['tier'], leagueData['rank'], leagueData['leaguePoints'])
                tier = leagueData['tier']
                rank = leagueData['rank']
                points = leagueData['leaguePoints']
                wins = leagueData['wins']
                losses = leagueData['losses']
                winrate = winrate
                progress = currentLP - startingLP
                progressDelta = progress - oldProgress
                streak = getPlayerStreakData(playerName, validPuuid, region, queueType)
                return tier, rank, points, wins, losses, winrate, progress, progressDelta, streak
    except Exception as ex:
        print("Exception {0} ocurred while looking up player {1}".format(type(ex).__name__, playerName))
        traceback.print_exc()

def getPlayerStreakData(playerName: str, puuid: str, region: str, queueType: int):
    queueNumber = constants.queueNameToQueueID[queueType]
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    count = 1
    streakString = ""
    correctedRegion = constants.platformToRegion[region.upper()]
    try:
        #FIXME: BUMP TO V5!!! V4 is deprecated
        #FIXME: I really, really hope there is a better way to do this. If not, we are going to run into ratelimits very easily.
        matchData = lolWatcher.match.matchlist_by_puuid(region=correctedRegion, puuid=puuid, count=5, queue=queueNumber)
        #matchData = lolWatcher.match_v4.matchlist_by_account(region=region, encrypted_account_id=puuid, queue=queueNumber, end_index=5)
        for match in matchData:
            print("[LeagueData] Processing match {0} for player {1}".format(count, playerName))
            count += 1
            gameData = lolWatcher.match.by_id(region=correctedRegion, match_id=match)
            for participant in gameData['info']['participants']:
                if (playerName == participant['summonerName']):
                    streakString += "W" if participant['win'] else "L"
    except Exception as ex:
        print("Exception {0} ocurred while looking up player {1}".format(type(ex).__name__, playerName))
        traceback.print_exc()
    finally:
        print("[LeagueData] Finished processing player {0}, streak is {1}".format(playerName, streakString))
        # since we read LTR, we reverse the string to put newest matches at the right.
        streakString = streakString[::-1]
        return streakString