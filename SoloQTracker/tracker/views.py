import asyncio
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from .forms import UserForm
from .updater.update_helper import UpdateHelper
from .models import Player, Challenge, Challenge_Player
from .forms import ChallengeForm
from .utils.validators import GenericNameValidator
from asgiref.sync import sync_to_async
# Create your views here.
def index(request): 
    return render(request, 'tracker/tracker.html')

async def player(request, player=""):
    if (player != ""):
        ourPlayer = Player.create(player, 'euw1')
        uh = UpdateHelper(ourPlayer)
        await uh.update()
    return HttpResponse('')

async def create_challenge(request):
    form = ChallengeForm()
    if (request.method == 'POST'):
        #TODO: Validation. Just testing for now, but needs error handling!
        print(request.POST)
        submitted_form = ChallengeForm(request.POST)
        #print(submitted_form.cleaned_data)
        #FIXME: Check is_valid and such, we are currently only using this for testing
        #TODO: Change to redirect to the newly created challenge.
        _name = request.POST['name']
        _start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%dT%H:%M')
        _end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%dT%H:%M')
        _player_region = list(zip(request.POST.getlist('player'), request.POST.getlist('region'))) 
        challenge = Challenge(name=_name, start_date=_start_date, end_date=_end_date, is_absolute=True)
        await sync_to_async(challenge.save)()
        tasks = []
        players = []
        player_challenges = []
        print(_player_region)
        for item in _player_region:
            print(item)
            #TODO: Check is player already exists. 
            player = Player.create(name=item[0], platform=item[1])
            players.append(player)
            uh = UpdateHelper(player)
            tasks.append(uh.update())
            player_challenge = Challenge_Player(player_id=player, challenge_id=challenge, starting_lp=0, starting_tier='IRON', starting_rank='IV')
            player_challenges.append(player_challenge)
        
        await sync_to_async(Player.objects.bulk_create)(players)
        await sync_to_async(Challenge_Player.objects.bulk_create)(player_challenges)
        await asyncio.gather(*tasks)        
        #challenge = Challenge(name=)
        return render(request, 'tracker/challenge_form.html', {'form': form}) 
    else:
        template = loader.get_template('tracker/challenge_form.html')
        
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
            #TODO: Use proper template user_validation.html
            return HttpResponse('Player found')
        except Exception:
            return HttpResponse('Player not found')
        
        
    
def challenge(request, id):
    #TODO: Implement this
    raise NotImplementedError

