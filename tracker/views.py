import os
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse
import riotwatcher
from tracker.models import LeagueData, MiscData
from django.views.generic import ListView

class LeagueDataListView(ListView):
    model = LeagueData
    template_name = 'tracker/tracker.html'

    def get_context_data(self, **kwargs):
        ctx = super(LeagueDataListView, self).get_context_data(**kwargs)
        ctx['date'] = MiscData.objects.first().date;
        return ctx

def index(request):
    if MiscData.objects.count() == 0:
        MiscData.objects.create(date=datetime.now)
    else:
        MiscData.objects.first().delete();
        MiscData.objects.create(date=datetime.now)
    if (request.method == 'POST'):
        for x in LeagueData.objects.all().iterator():
            x.delete()
        updateData()
        return redirect('tracker', permanent=False)
    else:
        return redirect('tracker', permanent=False)

def updateData():
    lolWatcher = riotwatcher.LolWatcher(os.environ.get("API_KEY"))
    region = os.environ.get("REGION");
    playernames = os.environ.get("PLAYERS").split(",");
    for str in playernames:
        summonerData = lolWatcher.summoner.by_name(region, str);
        allLeagueData = lolWatcher.league.by_summoner(region, summonerData['id'])

        for element in allLeagueData:
            if (element['queueType'] == "RANKED_SOLO_5x5"):
                leagueData = element;
                LeagueData.objects.create(name=summonerData['name'], tier=leagueData['tier'], rank=leagueData['rank'],
                                          points=leagueData['leaguePoints'], wins=leagueData['wins'],
                                          losses=leagueData['losses'])