import django_tables2 as tables
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from tracker.utils import constants
from .models import Challenge_Player, Challenge, Player

# TODO: Once multiple Challenge support is added, add filtering to this table. Else, add one view per challenge.
# About filtering: https://django-tables2.readthedocs.io/en/latest/pages/filtering.html
# Dynamic views: https://stackoverflow.com/a/49341050

class ChallengeTable(tables.Table):
    # There is no way to set a default column style in django-tables2, apparently. Fuck DRY
    column_style = {"cell": {"class": "m-2 p-2 border border-white border-collapse whitespace-nowrap"}}
    name = tables.Column(accessor="player_id.name", attrs=column_style)
    tier = tables.Column(accessor="player_id.tier", attrs=column_style)
    rank = tables.Column(accessor="player_id.rank", attrs=column_style)
    lp = tables.Column(accessor="player_id.lp", attrs=column_style)
    wins = tables.Column(accessor="player_id.wins", attrs=column_style)
    losses = tables.Column(accessor="player_id.losses", attrs=column_style)
    winrate = tables.Column(accessor="player_id.winrate", attrs=column_style)
    progress = tables.Column(accessor="progress", attrs=column_style)

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table-auto border-collapse border border-white text-white text-center"}
        row_attrs = {"class": "border border-white border-collapse"}
        order_by = "-progress"
        orderable = False  # disable header clicking

    def render_name(self, value):
        streak_string = ""
        platform = "EUW1"  # default
        playerName = "" + value
        playerName = playerName.strip()
        try:
            player = Player.objects.get(name=playerName)
            platform = player.platform
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
            constants.riotToOPGGRegions[platform.upper()], sanitized_name, value, streak_string))

    def render_winrate(self, value):
        if value >= 0.5:
            style = "color:rgb(180, 210, 115);"
        elif value < 0.5:
            style =  "color:rgb(249,36,114);"
        return format_html('<span style="{0}">{1:.2f}%</span>'.format(style, value))

    def render_progress (self, value, record):
        progress_style =  "color:rgb(180, 210, 115);" if (record.progress >= 0) else "color:rgb(249,36,114);"
        progress_delta_style = "color:rgb(180, 210, 115);" if (record.progress_delta >= 0) else "color:rgb(249,36,114);"
        progress_sign = "+" if (record.progress >= 0) else ""
        progress_delta_sign = "+" if (record.progress_delta >= 0) else ""
        return format_html('<span style="{0}">{1}{2}LP</span> <span style="{3}">({4}{5})</span>'.format(progress_style, 
                                                                                                    progress_sign, 
                                                                                                    value,
                                                                                                    progress_delta_style, 
                                                                                                    progress_delta_sign,
                                                                                                    record.progress_delta))
