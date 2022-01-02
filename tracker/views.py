import threading
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
    #model = LeagueData
    table_class = LeagueTable
    queryset = LeagueData.objects.filter(tracked__ignored=False)
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
        # Ignore if last update was less than 30 seconds ago.
        if (lastUpdateTimeDelta < timedelta(seconds=30)):
            print('[Index] Last updated less than a minute ago, ignoring.')
            return redirect('tracker', permanent=False)
        # Delete players that are not present in the model anymore
        for leaguePlayer in LeagueData.objects.all():
            try:
                trackedPlayer = TrackedPlayers.objects.get(pk=leaguePlayer.name)
            except ObjectDoesNotExist:
                print("[TrackedPlayer] Player {0} exists in ranking table but isn't tracked anymore, deleting...".format(leaguePlayer.name))
                leaguePlayer.delete()
        # Update all the player ranks and stats
        for trackedPlayer in TrackedPlayers.objects.all():
            if trackedPlayer.ignored:
                # Ignore the player, using if not might be more logic but this saves an indentation level which looks better.
                print("[LeagueData] Player {0} is in ignored list, continuing...".format(trackedPlayer.name))
                continue
            try:
                leaguePlayer = LeagueData.objects.get(pk=trackedPlayer.name)
                if not trackedPlayer.ignored:
                    tier, rank, points, wins, losses, winrate, progress, progressDelta, streak = updatePlayerData(trackedPlayer.name, trackedPlayer.puuid, trackedPlayer.accountId, trackedPlayer.id, trackedPlayer.region, queueType, trackedPlayer.startingTier, trackedPlayer.startingRank,
                                     trackedPlayer.startingPoints, leaguePlayer.progressDelta)
                    leaguePlayer.tier = tier
                    leaguePlayer.rank = rank
                    leaguePlayer.points = points
                    leaguePlayer.wins = wins
                    leaguePlayer.losses = losses
                    leaguePlayer.winrate = winrate
                    leaguePlayer.progress = progress
                    leaguePlayer.progressDelta = progressDelta
                    leaguePlayer.streak = streak
                    leaguePlayer.puuid = trackedPlayer.puuid
                    print("[LeagueData] Successfully updated existing player", trackedPlayer.name)
                    leaguePlayer.save()
            except ObjectDoesNotExist:
                try:
                    tier, rank, points, wins, losses, winrate, progress, progressDelta, streak = updatePlayerData(
                        trackedPlayer.name, trackedPlayer.puuid, trackedPlayer.accountId, trackedPlayer.id, trackedPlayer.region, queueType,
                        trackedPlayer.startingTier, trackedPlayer.startingRank,
                        trackedPlayer.startingPoints, 0)
                    leaguePlayer = LeagueData.objects.create(name=trackedPlayer.name, puuid=trackedPlayer.puuid, tier=tier,
                                                             rank=rank,
                                                             points=points, wins=wins,
                                                             losses=losses, winrate=winrate,
                                                             progress=0, progressDelta=0)
                    print("[LeagueData] Successfully created non-existing player", trackedPlayer.name)
                except TypeError:
                    print("[LeagueData] Error getting data for non-existing player ", trackedPlayer.name)
                    continue
            except TypeError:
                print("[LeagueData] Error getting data for player ", trackedPlayer.name)
                continue
            finally:
                leaguePlayer.save()
        challenge.lastUpdate = make_aware(datetime.now())
        challenge.save()
        return redirect('tracker', permanent=False)
    except Exception as ex:
        print("Exception {0} ocurred while updating data.".format(type(ex).__name__))
        traceback.print_exc()
        return redirect('error', permanent=False)

def error(request):
    template = loader.get_template('tracker/error.html')
    return HttpResponse(template.render())
