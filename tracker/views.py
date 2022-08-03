import asyncio
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.template import loader
from .forms import PlayerForm
from .updater.user_updater import UserUpdater
from .updater import updater_jobs
from .models import Player, Challenge, Challenge_Player
from .forms import ChallengeForm
from asgiref.sync import sync_to_async
from .tables import ChallengeTable
import uuid
from django_htmx.http import HttpResponseClientRedirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.cache import cache_page
from django_rq import get_queue


@cache_page(60 * 15)
@require_GET
def index(request):
    return render(request, "tracker/index.html")


@require_GET
def error(request):
    msg = messages.get_messages(request)
    code = ""
    for item in msg:
        if item.tags == "error":
            code = item
            break
    return render(request, "tracker/error.html", context=locals())


# Async views can't have required method decorators, so this will show up as an issue on SonarQube for a while.
# TODO: This can be problematic since it runs on the server thread and makes API calls, maybe do all updates on UpdaterThread?
async def create_challenge(request):
    form = ChallengeForm()
    if request.method == "POST":
        # TODO: Validation. Just testing for now, but needs error handling!
        print(request.POST)
        submitted_form = ChallengeForm(request.POST)
        # print(submitted_form.cleaned_data)
        # FIXME: Check is_valid and such, we are currently only using this for testing
        if not form.is_valid:
            messages.error(request, "400")
            return redirect(reverse("error"))
        _name = request.POST["name"]
        _start_date = datetime.strptime(request.POST["start_date"], "%Y-%m-%dT%H:%M")
        _end_date = datetime.strptime(request.POST["end_date"], "%Y-%m-%dT%H:%M")
        _player_platform = list(zip(request.POST.getlist("player_name"), request.POST.getlist("platform")))
        _is_absolute = "is_absolute" in request.POST.keys()
        _ignore_unranked = "ignore_unranked" in request.POST.keys()
        queue = get_queue("high")
        job = queue.enqueue(
            updater_jobs.create_challenge_job,
            kwargs={
                "name": _name,
                "start_date": _start_date,
                "end_date": _end_date,
                "player_platform": _player_platform,
                "is_absolute": _is_absolute,
                "ignore_unranked": _ignore_unranked,
            },
        )
        return redirect("challenge", challenge_id=challenge.id)
    else:
        return render(request, "tracker/challenge_form.html", {"form": form})


@require_GET
def create_user_form(request):
    form_id = uuid.uuid4()
    form = PlayerForm(form_id=form_id)

    return render(request, "tracker/partials/user_form.html", context=locals())


async def provisional_parse(request):
    # FIXME: Broken
    if request.method == "POST":
        print(request.POST)
        if "player_name" not in request.POST.keys() or "platform" not in request.POST.keys():
            return HttpResponse("")
        player_name = request.POST.get("player_name", "")
        platform = request.POST.get("platform", "")
        try:
            player = await sync_to_async(Player.objects.get)(name=player_name, platform=platform)
            exists = True
            # TODO: We return here to prevent an unneeded update in finally. Maybe take this out of try to prevent a code smell.
            return render(request, "tracker/partials/user_validation.html", context=locals())
        except Player.DoesNotExist:
            player = Player.create(player_name, platform)
        finally:
            uu = UserUpdater(player)
            try:
                player_data = await uu.backend.get_player_data(player)
                player.avatar_id = player_data["profileIconId"]
                exists = True
            except Exception:
                exists = False

        return render(request, "tracker/partials/user_validation.html", context=locals())


@cache_page(60 * 15)
@require_http_methods(["GET", "POST"])
def challenge(request, challenge_id=0):
    if request.htmx and challenge_id == 0:
        challenge_id = request.POST.get("search_input", None)
        return HttpResponseClientRedirect(reverse("challenge") + "{0}/".format(challenge_id))  # FIXME: Janky as fuck
        # FIXME: Error handling here.
    try:
        challenge_data = Challenge.objects.get(id=challenge_id)
        if challenge_data.ignore_unranked:
            player_query = (
                Challenge_Player.objects.filter(challenge_id=challenge_id)
                .exclude(player_id__tier="UNRANKED")
                .select_related("player_id")
                .order_by("-progress")
            )
        else:
            player_query = (
                Challenge_Player.objects.filter(challenge_id=challenge_id)
                .exclude(ignored=True)
                .select_related("player_id")
                .order_by("-progress")
            )
        table = ChallengeTable(player_query)
        right_now = timezone.now()
        start_date = challenge_data.start_date
        end_date = challenge_data.end_date
        challenge_name = challenge_data.name
        challenge_id = challenge_data.id
        if right_now >= start_date:
            challenge_status = "Ongoing"
        elif right_now >= end_date:
            challenge_status = "Scheduled"
        else:
            challenge_status = "Done"
    except Exception:
        messages.error(request, "404")
        return redirect(reverse("error"))
    return render(request, "tracker/challenge.html", context=locals())


@cache_page(60 * 15)
@require_GET
def search(request):
    return render(request, "tracker/partials/search_modal.html")
