import django_tables2 as tables
from django.utils.html import format_html

from .models import LeagueData

#TODO: Once multiple Challenge support is added, add filtering to this table.
class LeagueTable(tables.Table):
    class Meta:
        model = LeagueData
        template_name = "django_tables2/bootstrap.html"
        fields = ("name", "tier", "rank", "points", "wins", "losses", "winrate", "progress")
        attrs = {"class": "ranktable"}
        orderable = False  # disable header clicking
    def render_name(self, value, column):
        #TODO: This is currently hardcoded to be EUW OPGG.
        sanitized_name = value.replace(" ", "+")
        return format_html('<a href=https://euw.op.gg/summoner/userName={0}>{1}</a>'.format(sanitized_name, value))

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


