from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from .forms import UserForm
from .updater.update_helper import UpdateHelper
from .models import Player
from .forms import ChallengeForm
from .utils.validators import GenericNameValidator
# Create your views here.
def index(request): 
    return render(request, 'tracker/tracker.html')

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

def create_user_form(request):
    form = UserForm()
    context = {
        "form": form
    }
    return render(request, "tracker/partials/user_form.html", context)

async def provisional_parse(request):
    if (request.method == 'POST'):
        if ('player' not in request.POST.keys() or 'region' not in request.POST.keys() or not GenericNameValidator(request.POST['player'])):
            return HttpResponse('')
        player = Player.create(request.POST['player'], request.POST['region'])
        uh = UpdateHelper(player)
        try:
            await uh.get_player_data()
            return HttpResponse('Player found')
        except Exception:
            return HttpResponse('Player not found')
        
        
    
def challenge(request, id):
    raise NotImplementedError

