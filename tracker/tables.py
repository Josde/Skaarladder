import django_tables2 as tables
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from . import constants
from .models import LeagueData, TrackedPlayers


#TODO: Once multiple Challenge support is added, add filtering to this table.
#About filtering: https://django-tables2.readthedocs.io/en/latest/pages/filtering.html
class LeagueTable(tables.Table):
    class Meta:
        model = LeagueData
        template_name = "django_tables2/bootstrap.html"
        fields = ("name", "tier", "rank", "points", "wins", "losses", "winrate", "progress")
        attrs = {"class": "ranktable"}
        orderable = False  # disable header clicking

    def render_name(self, value, column):
        region = "EUW1" #default
        try:
            player = TrackedPlayers.objects.get(name=value)
            region = player.region
        except ObjectDoesNotExist:
            print("[LeagueTable] Rendering a player that can't be found in TrackedPlayers. This shouldn't happen.")
        sanitized_name = value.replace(" ", "+")
        return format_html('<a href=https://{0}.op.gg/summoner/userName={1}>{2}</a>'.format(constants.riotToOPGGRegions[region.upper()], sanitized_name, value))

    def render_winrate(self, value, column):
        if value > 0.5:
            column.attrs = {'td': {'style': 'color:green'}}
        elif value < 0.5:
            column.attrs = {'td': {'style': 'color:red'}}
        return "{:0.2f}%".format(value * 100)

    def render_progress(self, value, column):
        if value > 0:
            column.attrs = {'td': {'style': 'color:green'}}
        elif value < 0:
            column.attrs = {'td': {'style': 'color:red'}}
        return "{0}LP".format(value)


