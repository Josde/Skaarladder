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
        player.id = id
        player.accountId = accountId
        player.puuid = puuid
        print("[UpdateIds] New IDs for player {0}: {1} // {2} // {3}".format(player.name, id, accountId, puuid))
        player.save()

def getIds(playerName, region):
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    try:
        summonerData = lolWatcher.summoner.by_name(region, playerName)
        return summonerData['id'], summonerData['accountId'], summonerData['puuid']
    except Exception:
        return ["", "", ""]


def updatePlayerData(playerName, accountId, id, region, queueType, startingTier, startingRank, startingPoints, oldProgressDelta):
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    try:
        if len(accountId) < 20 or len(id) < 20: #validity check, idk if theres a documented minimum
            summonerData = lolWatcher.summoner.by_name(region, playerName)
            validId = summonerData['id']
            validAccountId = summonerData['accountId']
        else:
            validId = id
            validAccountId = accountId
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
                progressDelta = progress - oldProgressDelta
                streak = getPlayerStreakData(playerName, validAccountId, region, queueType)
                return tier, rank, points, wins, losses, winrate, progress, progressDelta, streak
    except Exception as ex:
        print("Exception {0} ocurred while looking up player {1}".format(type(ex).__name__, playerName))
        traceback.print_exc()

def getPlayerStreakData(playerName, puuid, region, queueType):
    queueNumber = constants.queueNameToQueueID[queueType]
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    count = 1
    streakString = ""
    correctedRegion = constants.platformToRegion[region]
    try:
        #FIXME: BUMP TO V5!!! V4 is deprecated
        #FIXME: I really, really hope there is a better way to do this. If not, we are going to run into ratelimits very easily.
        matchData = lolWatcher.match.matchlist_by_puuid(region=correctedRegion, puuid=puuid, count=5, queue=queueNumber)
        #matchData = lolWatcher.match_v4.matchlist_by_account(region=region, encrypted_account_id=puuid, queue=queueNumber, end_index=5)
        # This API is fucking horrid, just what is this level of nesting structs
        for match in matchData['matches']:
            print("[LeagueData] Processing match {0} for player {1}".format(count, playerName))
            count += 1
            gameData = lolWatcher.match.by_id(region=region, match_id=match['gameId'])
            for participant, participantID in zip(gameData['participants'], gameData['participantIdentities']):
                participantStats = participant['stats']
                participantPlayerData = participantID['player']
                if (playerName == participantPlayerData['summonerName']):
                    streakString += "W" if participantStats['win'] else "L"
    except Exception as ex:
        print("Exception {0} ocurred while looking up player {1}".format(type(ex).__name__, playerName))
        traceback.print_exc()
    finally:
        print("[LeagueData] Finished processing player {0}, streak is {1}".format(playerName, streakString))
        return streakString