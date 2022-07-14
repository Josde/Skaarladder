from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from tracker.updater.update_helper import UpdateHelper
from tracker.models import Player
# Create your views here.
def index(request): 
    template = loader.get_template('tracker/tracker.html')
    return HttpResponse(template.render())

async def player(request, player=""):
    if (player != ""):
        ourPlayer = Player.create(player, 'euw1')
        uh = UpdateHelper(ourPlayer)
        await uh.update()
    return HttpResponse('')
