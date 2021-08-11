import os
import traceback

import riotwatcher
from django.core.exceptions import *

from . import constants
from .models import LeagueData


def rankToLP(rank, tier, points):
    return (constants.rankWeights[rank]) * 400 + (constants.tierWeights[tier]) * 100 + int(points)

def getIds(playerName, region):
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    try:
        summonerData = lolWatcher.summoner.by_name(region, playerName)
        return summonerData['id'], summonerData['accountId'], summonerData['puuid']
    except Exception:
        return ""

def updatePlayerData(playerName, accountId, id, region, queueType, startingTier, startingRank, startingPoints, oldProgressDelta):
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    try:
        summonerData = lolWatcher.summoner.by_name(region, playerName)
        print(summonerData)
        if len(puuid) < 20: #validity check, idk if theres a documented minimum
            summonerData = lolWatcher.summoner.by_name(region, playerName)
            validPuuid = summonerData['id']
        else:
            validPuuid = puuid
        allLeagueData = lolWatcher.league.by_summoner(region, puuid)
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
                streak = getPlayerStreakData(playerName, validPuuid, region, queueType)
                return tier, rank, points, wins, losses, winrate, progress, progressDelta, streak
    except Exception as ex:
        print("Exception {0} ocurred while looking up player {1}".format(type(ex).__name__, playerName))
        traceback.print_exc()

def getPlayerStreakData(playerName, puuid, region, queueType):
    queueNumber = constants.queueNameToQueueID[queueType]
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    count = 1
    streakString = ""
    try:
        #FIXME: bump to v5 before august, when riotwatcher updates
        #FIXME: I really, really hope there is a better way to do this. If not, we are going to run into ratelimits very easily.
        #matchData = lolWatcher.match_v5.matchlist_by_puuid(region=region, puuid=puuid, count=5, queue=queueNumber) # this requires a region name update / dict because riot is fucking annoying
        matchData = lolWatcher.match_v4.matchlist_by_account(region=region, encrypted_account_id=puuid, queue=queueNumber, end_index=5)
        # This API is fucking horrid, just what is this level of nesting structs
        for match in matchData['matches']:
            print("[LeagueData] Processing match {0} for player {1}".format(count, playerName))
            count += 1
            gameData = lolWatcher.match_v4.by_id(region=region, match_id=match['gameId'])
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