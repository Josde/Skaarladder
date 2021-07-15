import os
from datetime import datetime, timedelta
from .tables import LeagueTable
from django.shortcuts import render, redirect
from django.http import HttpResponse
import riotwatcher
from tracker.models import LeagueData, TrackedPlayers
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
            if len(players) != 0:
                ctx['bottomMessage'] = "🎉🎉 El ganador es... ¡¡{0}!! 🎉🎉".format(players[0].name)
            else:
                ctx['bottomMessage'] = "El reto ya ha acabado."
        return ctx



def index(request):
    if (request.method == 'POST'):
        queueType = os.getenv("QUEUE_TYPE", default="RANKED_SOLO_5x5")
        for player in TrackedPlayers.objects.all():
            updatePlayerData(player.name, player.region, queueType, player.startingTier, player.startingRank, player.startingPoints)
        return redirect('tracker', permanent=False)
    else:
        return redirect('tracker', permanent=False)




