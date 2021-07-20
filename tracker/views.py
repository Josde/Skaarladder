from datetime import datetime, timedelta, date
from datetime import datetime, timedelta, date

from django.shortcuts import redirect
from django_tables2 import SingleTableView

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
        # TODO: CurrentDate currently doesn't represent the last update time like it should.
        ctx['currentDate'] = datetime.now().strftime("%d %B, %Y, %H:%M:%S")
        ctx['endDate'] = challenge.endDate
        timeDelta = challenge.endDate - date.today()
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
    if request.method == 'POST':
        queueType = os.getenv("QUEUE_TYPE", default="RANKED_SOLO_5x5")
        for player in TrackedPlayers.objects.all():
            if not player.ignored:
                updatePlayerData(player.name, player.region, queueType, player.startingTier, player.startingRank,
                                 player.startingPoints)
        return redirect('tracker', permanent=False)
    else:
        return redirect('tracker', permanent=False)
