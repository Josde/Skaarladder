from datetime import datetime, timedelta, date

from django.shortcuts import redirect
from django.utils.timezone import make_aware
from django_tables2 import SingleTableView
from django.template import loader
from django.http import HttpResponse
from tracker.models import TrackedPlayers, Challenge
from .misc import *
from .tables import LeagueTable


class LeagueDataListView(SingleTableView):
    model = LeagueData
    table_class = LeagueTable
    template_name = 'tracker/tracker.html'
    ordering = "-progress"

    def get_context_data(self, **kwargs):
        # This will never give an error because if no challenges are registered, we make one on ready()
        challenge = Challenge.objects.first()
        ctx = super(LeagueDataListView, self).get_context_data(**kwargs)
        ctx['currentDate'] = challenge.lastUpdate
        ctx['endDate'] = challenge.endDate
        timeDelta = challenge.endDate - date.today()
        #TODO: Refactor bottomMessage into multiple strings to make it fully configurable from HTML.
        if timeDelta > timedelta(seconds=0):
            hours, rem = divmod(timeDelta.seconds, 3600)
            mins, secs = divmod(rem, 60)
            ctx['bottomMessage'] = "Quedan {0} dias, {1} horas y {2} minutos".format(timeDelta.days, hours, mins)
        else:
            players = self.model.objects.order_by('-progress')
            if len(players) != 0:
                ctx['bottomMessage'] = "🎉🎉 El ganador es... ¡¡{0}!! 🎉🎉".format(players[0].name)
            else:
                ctx['bottomMessage'] = "El reto ya ha acabado."
        return ctx

def index(request):
    try:
        challenge = Challenge.objects.first()
        queueType = challenge.queueType
        lastUpdateTimeDelta = make_aware(datetime.now()) - challenge.lastUpdate
        if (lastUpdateTimeDelta < timedelta(seconds=30)):
            print('[Index] Last updated less than 30 seconds ago, ignoring.')
            return redirect('tracker', permanent=False)
        else: #unneeded but for clarity
            for trackedPlayer in TrackedPlayers.objects.all():
                if not trackedPlayer.ignored:
                    try:
                        player = LeagueData.objects.get(name=trackedPlayer.name)
                        tier, rank, points, wins, losses, winrate, progress, progressDelta, streak = updatePlayerData(
                            trackedPlayer.name, trackedPlayer.region, queueType, trackedPlayer.startingTier, trackedPlayer.startingRank,
                            trackedPlayer.startingPoints, player.progressDelta)
                        player.tier = tier
                        player.rank = rank
                        player.points = points
                        player.wins = wins
                        player.losses = losses
                        player.winrate = winrate
                        player.progress = progress
                        player.progressDelta = progressDelta
                        player.streak = streak
                        player.save()
                        print("[LeagueData] Successfully updated existing player", player.name)
                    except ObjectDoesNotExist:
                        player = LeagueData.objects.create(name=trackedPlayer.name)
                        tier, rank, points, wins, losses, winrate, progress, progressDelta, streak = updatePlayerData(
                            trackedPlayer.name, trackedPlayer.region, queueType, trackedPlayer.startingTier,
                            trackedPlayer.startingRank,
                            trackedPlayer.startingPoints, player.progressDelta)
                        player.tier = tier
                        player.rank = rank
                        player.points = points
                        player.wins = wins
                        player.losses = losses
                        player.winrate = winrate
                        player.progress = progress
                        player.progressDelta = progressDelta
                        player.streak = streak
                        player.save()
                        print("[LeagueData] Successfully created non-existing player", trackedPlayer.name)
            challenge = Challenge.objects.first()
            challenge.lastUpdate = make_aware(datetime.now())
            challenge.save()
            return redirect('tracker', permanent=False)
    except Exception as ex:
        print("Exception {0} ocurred while updating data".format(type(ex).__name__))
        traceback.print_exc()
        return redirect('error', permanent=False)

#TODO: Make error page not a placeholder.
def error(request):
    template = loader.get_template('tracker/error.html')
    return HttpResponse(template.render())
