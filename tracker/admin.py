from django.contrib import admin
from tracker.models import Player, Ladder_Player, Ladder

# Register your models here.
admin.site.register([Player, Ladder_Player, Ladder])
