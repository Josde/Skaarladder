import django_tables2 as tables
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from tracker.utils import constants
from .models import Player


class LadderTable(tables.Table):
    # There is no way to set a default column style in django-tables2, apparently. Fuck DRY
    column_style = {"cell": {"class": "m-4 p-4 border border-neutral-500 border-collapse whitespace-nowrap"}}
    name = tables.Column(accessor="player_id__name", attrs=column_style)
    tier = tables.Column(accessor="player_id__tier", attrs=column_style)
    rank = tables.Column(accessor="player_id__rank", attrs=column_style)
    lp = tables.Column(accessor="player_id__lp", attrs=column_style)
    wins = tables.Column(accessor="player_id__wins", attrs=column_style)
    losses = tables.Column(accessor="player_id__losses", attrs=column_style)
    winrate = tables.Column(accessor="player_id__winrate", attrs=column_style)
    progress = tables.Column(accessor="progress", attrs=column_style)

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table-auto border-collapse border border-neutral-500 text-white text-start "}
        row_attrs = {"class": "border border-white border-collapse"}
        orderable = False  # disable header clicking

    def render_name(self, value, record):
        streak_string = ""
        platform = "EUW1"  # default
        player_name = "" + value
        player_name = player_name.strip()
        try:
            player = Player.objects.get(name=player_name)
            platform = player.platform
            streak = player.streak
            avatar_id = player.avatar_id
            if 1 > streak > -1:
                streak_string = ""
            elif streak > 1:
                streak_string = '<span style="{0}">{1}W</span>'.format(constants.green_text_style, streak)
            elif streak < -1:
                streak_string = '<span style="{0}">{1}L</span>'.format(constants.red_text_style, abs(streak))

        except ObjectDoesNotExist:
            print(
                "[LeagueTable] Rendering player {0}, who can't be found in TrackedPlayers. \
                    This shouldn't happen.".format(
                    value
                )
            )
        except Player.MultipleObjectsReturned:
            player = Player.objects.all().filter(name=player_name)[0]
        sanitized_name = value.replace(" ", "+")
        return format_html(
            """<img class="inline w-10 h-10" onerror="this.style.display='none'" 
                           src="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{0}.jpg"> </img>
                           <a href=https://{1}.op.gg/summoner/userName={2}>{3}</a> {4}""".format(
                avatar_id,
                constants.riotToOPGGRegions[platform.upper()],
                sanitized_name,
                value,
                streak_string,
            )
        )

    def render_winrate(self, value):
        if value >= 0.5:
            style = constants.green_text_style
        elif value < 0.5:
            style = constants.red_text_style
        return format_html('<span style="{0}">{1:.2f}%</span>'.format(style, value))

    def render_progress(self, value, record):
        progress_style = constants.green_text_style if (record.progress >= 0) else constants.red_text_style
        progress_delta_style = constants.green_text_style if (record.progress_delta >= 0) else constants.red_text_style
        progress_sign = "+" if (record.progress >= 0) else ""
        progress_delta_sign = "+" if (record.progress_delta >= 0) else ""
        return format_html(
            '<span style="{0}">{1}{2}LP</span> <span style="{3}">({4}{5})</span>'.format(
                progress_style,
                progress_sign,
                value,
                progress_delta_style,
                progress_delta_sign,
                record.progress_delta,
            )
        )
