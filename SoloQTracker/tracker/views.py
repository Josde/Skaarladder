import asyncio
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from .forms import PlayerForm
from .updater.update_helper import UpdateHelper
from .models import Player, Challenge, Challenge_Player
from .forms import ChallengeForm
from .utils.validators import GenericNameValidator
from asgiref.sync import sync_to_async
from .tables import ChallengeTable
import uuid
# Create your views here.
def index(request): 
    return render(request, 'tracker/index.html')

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
        _player_platform = list(zip(request.POST.getlist('player_name'), request.POST.getlist('platform'))) 
        challenge = Challenge(name=_name, start_date=_start_date, end_date=_end_date, is_absolute=True)
        await sync_to_async(challenge.save)()
        tasks = []
        players = []
        player_challenges = []
        for item in _player_platform:
            if (len(item) < 2):
                return render(request, 'tracker/error.html') #FIXME: Temporal
            print("Searching player {0} {1}".format(item[0], item[1]))
            try:
                
                player = await sync_to_async(Player.objects.get)(name=item[0], platform=item[1])
                print("Found")
            except Player.DoesNotExist:
                player = Player.create(name=item[0], platform=item[1])
                players.append(player) # We only created non existing players to prevent violating PK uniqueness
            finally:
                uh = UpdateHelper(player)
                tasks.append(uh.update())
                # Fixme: Add starting rank
                player_challenge = Challenge_Player(player_id=player, challenge_id=challenge, starting_lp=0, starting_tier='IRON', starting_rank='IV')
                player_challenges.append(player_challenge)
        
        await sync_to_async(Player.objects.bulk_create)(players)
        await sync_to_async(Challenge_Player.objects.bulk_create)(player_challenges)
        await asyncio.gather(*tasks)        
        return redirect('challenge', id=challenge.id)
    else:
        template = loader.get_template('tracker/challenge_form.html')
        
        return render(request, 'tracker/challenge_form.html', {'form': form}) 

def create_user_form(request):
    form_id = uuid.uuid4()
    form = PlayerForm(form_id=form_id)

    return render(request, "tracker/partials/user_form.html", context=locals())

async def provisional_parse(request):
    if (request.method == 'POST'):
        if ('player_name' not in request.POST.keys() or 'platform' not in request.POST.keys()):
            return HttpResponse('')
        try: 
            player = await sync_to_async(Player.objects.get)(name=request.POST['player_name'], platform=request.POST['platform']) #TODO: Cleanup
            exists = True
            return render(request, 'tracker/partials/user_validation.html', context=locals())
        except Player.DoesNotExist:
            player = Player.create(request.POST['player_name'], request.POST['platform'])
        finally:
            uh = UpdateHelper(player)
            try:
                player_data = await uh.get_player_data()
                player.avatar_id = player_data['profileIconId']
                exists = True
                #TODO: Use proper template user_validation.html
                return render(request, 'tracker/partials/user_validation.html', context=locals())
            except Exception:
                exists = False
                return render(request, 'tracker/partials/user_validation.html', context=locals())
        
        
    
def challenge(request, id):
    challenge_data = Challenge.objects.filter(id=id).first()
    player_query = Challenge_Player.objects.filter(challenge_id=id).select_related('player_id').order_by('-progress')
    table = ChallengeTable(player_query)
    start_date = challenge_data.start_date
    end_date = challenge_data.end_date
    challenge_name = challenge_data.name 
    return render(request, 'tracker/challenge.html', context=locals())

