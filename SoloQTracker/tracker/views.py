from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from tracker.updater.update_helper import UpdateHelper
from tracker.models import Player
from tracker.forms import ChallengeForm
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

def create_challenge(request):
    if (request.method == 'POST'):
        #processing stuff
        submitted_form = ChallengeForm(request.POST)
        raise NotImplementedError
    else:
        template = loader.get_template('tracker/challenge_form.html')
        form = ChallengeForm()
        return render(request, 'tracker/challenge_form.html', {'form': form}) 

def challenge(request, id):
    raise NotImplementedError