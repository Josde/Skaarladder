from django.contrib import admin
from tracker.models import Player, Challenge_Player, Challenge
# Register your models here.
admin.site.register([Player, Challenge_Player, Challenge])