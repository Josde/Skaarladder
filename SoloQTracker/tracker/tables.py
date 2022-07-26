import django_tables2 as tables
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from tracker.utils import constants
from .models import Challenge_Player, Challenge, Player

# TODO: Once multiple Challenge support is added, add filtering to this table. Else, add one view per challenge.
# About filtering: https://django-tables2.readthedocs.io/en/latest/pages/filtering.html
# Dynamic views: https://stackoverflow.com/a/49341050

class ChallengeTable(tables.Table):
    name = tables.Column(accessor="player_id.name")
    tier = tables.Column(accessor="player_id.tier")
    rank = tables.Column(accessor="player_id.rank")
    lp = tables.Column(accessor="player_id.lp")
    wins = tables.Column(accessor="player_id.wins")
    losses = tables.Column(accessor="player_id.losses")
    winrate = tables.Column(accessor="player_id.winrate")
    progress = tables.Column(accessor="progress")

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "border-collapse text-white text-center"}
        order_by = "-progress"
        orderable = False  # disable header clicking

    def render_name(self, value, column):
        streak_string = ""
        region = "EUW1"  # default
        playerName = "" + value
        playerName = playerName.strip()
        column.attrs = {'td': {'class': 'whitespace-nowrap'}}
        try:
            player = Player.objects.get(name=playerName)
            region = player.platform
            streak = player.streak
            if streak < 1 and streak > -1:
                streak_string = ""
            elif streak > 1:
                streak_string = '<span style="color:rgb(180, 210, 115);">{0}L</span>'.format(streak) # TODO: For some reason styling this with a tailwind class doesn't work, check later.
            elif streak < -1:
                streak_string = '<span style="color:rgb(249,36,114);">{0}W</span>'.format(streak)
        
        except ObjectDoesNotExist:
            print("[LeagueTable] Rendering player {0}, who can't be found in TrackedPlayers. This shouldn't happen.".format(value))
        sanitized_name = value.replace(" ", "+")
        return format_html('<a href=https://{0}.op.gg/summoner/userName={1}>{2}</a> {3}'.format(
            constants.riotToOPGGRegions[region.upper()], sanitized_name, value, streak_string))

    def render_winrate(self, value, column):
        if value >= 0.5:
            column.attrs = {'td': {'style': 'color:rgb(180, 210, 115);'}}
        elif value < 0.5:
            column.attrs = {'td': {'style': 'color:rgb(249,36,114);'}}
        return "{:0.2f}%".format(value)

    def render_progress (self, value, column, record):
        column.attr = {'class': 'whitespace-nowrap'}
        if value > 0:
            column.attrs = column.attrs | {'td': {'style': 'color:rgb(180, 210, 115);'}}
        elif value < 0:
            column.attrs = column.attrs | {'td': {'style': 'color:rgb(249,36,114);'}}
        progressSign = "+" if (record.progress >= 0) else ""
        progressDeltaSign = "+" if (record.progress_delta >= 0) else ""
        return "{0}{1}LP ({2}{3})".format(progressSign, value, progressDeltaSign, record.progress_delta)
