import os
from datetime import datetime, timedelta
from .tables import LeagueTable
from django.shortcuts import render, redirect
from django.http import HttpResponse
import riotwatcher
from tracker.models import LeagueData
from django.views.generic import ListView
from django_tables2 import SingleTableView
from .misc import *
class LeagueDataListView(SingleTableView):
    model = LeagueData
    table_class = LeagueTable
    template_name = 'tracker/tracker.html'
    ordering = "-progress"

    def get_context_data(self, **kwargs):
        ctx = super(LeagueDataListView, self).get_context_data(**kwargs)
        ctx['date'] = datetime.now().strftime("%d %B, %Y, %H:%M:%S")
        timeDelta = datetime(int(os.getenv("ENDDATE_YEAR")), int(os.getenv("ENDDATE_MONTH")), int(os.getenv("ENDDATE_DAY"))) - datetime.now()
        if (timeDelta > timedelta(seconds=0)):
            hours, rem = divmod(timeDelta.seconds, 3600)
            mins, secs = divmod(rem, 60)
            ctx['bottomMessage'] = "Quedan {0} dias, {1} horas y {2} minutos".format(timeDelta.days, hours, mins)
        else:
            players = self.model.objects.order_by('-progress');
            ctx['bottomMessage'] = "🎉🎉 El ganador es... ¡¡{0}!! 🎉🎉".format(players[0].name);
        return ctx



def index(request):
    if (request.method == 'POST'):
        for x in LeagueData.objects.all().iterator():
            x.delete()
        updateData()
        return redirect('tracker', permanent=False)
    else:
        return redirect('tracker', permanent=False)


def updateData():
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    region = os.environ.get("REGION")
    playernames = os.environ.get("PLAYERS").split(",")
    startingRanks = os.environ.get("STARTING_RANKS").split(",")
    ignoredPlayers = os.environ.get("IGNORED_PLAYERS").split(",")
    for str, str2 in zip(playernames, startingRanks):
        summonerData = lolWatcher.summoner.by_name(region, str)
        allLeagueData = lolWatcher.league.by_summoner(region, summonerData['id'])
        startingRankSplit = list(filter(None, str2.split(" ")))
        if (str in ignoredPlayers): #skip players in ignored player list
            continue
        for element in allLeagueData:
            if (element['queueType'] == "RANKED_SOLO_5x5"):
                leagueData = element
                winrate = float(leagueData['wins']) / (leagueData['wins'] + float(leagueData['losses']))
                startingLP = rankToLP(startingRankSplit[0], startingRankSplit[1], startingRankSplit[2])
                currentLP = rankToLP(leagueData['tier'], leagueData['rank'], leagueData['leaguePoints'])
                LeagueData.objects.create(name=summonerData['name'], tier=leagueData['tier'], rank=leagueData['rank'],
                                          points=leagueData['leaguePoints'], wins=leagueData['wins'],
                                          losses=leagueData['losses'], winrate=winrate, progress=currentLP-startingLP)

