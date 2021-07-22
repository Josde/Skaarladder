import django_tables2 as tables
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from . import constants
from .models import LeagueData, TrackedPlayers


# TODO: Once multiple Challenge support is added, add filtering to this table. Else, add one view per challenge.
# About filtering: https://django-tables2.readthedocs.io/en/latest/pages/filtering.html
# Dynamic views: https://stackoverflow.com/a/49341050
class LeagueTable(tables.Table):
    class Meta:
        model = LeagueData
        template_name = "django_tables2/bootstrap.html"
        fields = ("name", "tier", "rank", "points", "wins", "losses", "winrate", "progress", "streak")
        attrs = {"class": "ranktable"}
        orderable = False  # disable header clicking

    def render_name(self, value):
        region = "EUW1"  # default
        try:
            player = TrackedPlayers.objects.get(name=value)
            region = player.region
        except ObjectDoesNotExist:
            print("[LeagueTable] Rendering a player that can't be found in TrackedPlayers. This shouldn't happen.")
        sanitized_name = value.replace(" ", "+")
        return format_html('<a href=https://{0}.op.gg/summoner/userName={1}>{2}</a>'.format(
            constants.riotToOPGGRegions[region.upper()], sanitized_name, value))

    def render_winrate(self, value, column):
        if value > 0.5:
            column.attrs = {'td': {'style': 'color:green'}}
        elif value < 0.5:
            column.attrs = {'td': {'style': 'color:red'}}
        return "{:0.2f}%".format(value * 100)

    def render_progress(self, value, column, record):
        if value > 0:
            column.attrs = {'td': {'style': 'color:green'}}
        elif value < 0:
            column.attrs = {'td': {'style': 'color:red'}}
        sign = "+" if (record.progressDelta >= 0) else "-"
        return "{0}LP ({1}{2})".format(value, sign, record.progressDelta)

    def render_streak(self, value):
        streak_string = "" + value
        new_string = ""
        for letter in streak_string:
            if letter == "W":
                new_string += '<span style="color:green">W</span>'
            elif letter == "L":
                new_string += '<span style="color:red">L</span>'
            else:
                new_string += letter
        return format_html(new_string)