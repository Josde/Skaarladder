import django_tables2 as tables

from .models import LeagueData


class LeagueTable(tables.Table):
    class Meta:
        model = LeagueData
        template_name = "django_tables2/bootstrap.html"
        fields = ("name", "tier", "rank", "points", "wins", "losses", "winrate", "progress")
        attrs = {"class": "ranktable"}
        orderable = False  # disable header clicking

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
