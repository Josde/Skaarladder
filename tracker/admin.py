from django.contrib import admin

from tracker.models import Ladder, Ladder_Player, Player

# Register your models here.
admin.site.register([Player, Ladder_Player, Ladder])
