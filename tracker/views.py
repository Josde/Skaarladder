import asyncio
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.template import loader

from tracker.updater import api_update_helper
from .forms import PlayerForm
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


async def create_challenge(request):
    if request.method == "POST":
        print(request.POST)
        submitted_form = ChallengeForm(request.POST)
        player_forms = []
        valid_player_forms = True
        _player_platform = list(
            zip(
                request.POST.getlist("player_name"),
                request.POST.getlist("platform"),
                request.POST.getlist("initial-is_valid"),
            )
        )
        for item in _player_platform:
            player_form = PlayerForm(
                form_id=uuid.uuid4(), initial={"player_name": item[0], "platform": item[1], "is_valid": item[2]}
            )
            player_form.data["player_name"] = item[0]
            player_form.data["platform"] = item[1]
            player_form.data["is_valid"] = item[2]
            if not player_form.is_valid():  # use the is_valid attribute to check if user exists too
                valid_player_forms = False
            player_forms.append(player_form)
        if len(player_forms) < 2:
            submitted_form.add_error("Must have at least 2 players in your ladder.")
        if not submitted_form.is_valid() or not valid_player_forms:
            return render(
                request, "tracker/challenge_form.html", {"form": submitted_form, "player_forms": player_forms}
            )

        _name = request.POST["name"]
        _start_date = datetime.strptime(request.POST["start_date"], "%Y-%m-%dT%H:%M")
        _end_date = datetime.strptime(request.POST["end_date"], "%Y-%m-%dT%H:%M")

        _is_absolute = "is_absolute" in request.POST.keys()
        _ignore_unranked = "ignore_unranked" in request.POST.keys()
        # if ()
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
        return redirect("challenge_loading", job_id=job.id)
    else:
        form = ChallengeForm()
        return render(request, "tracker/challenge_form.html", {"form": form})


@require_GET
def create_user_form(request):
    form_id = uuid.uuid4()
    form = PlayerForm(form_id=form_id)

    return render(request, "tracker/partials/user_form.html", context=locals())


async def provisional_parse(request):
    exists = False
    if request.method == "POST":
        print(request.POST)
        if "player_name" not in request.POST.keys() or "platform" not in request.POST.keys():
            return HttpResponse("")
        player_name = request.POST.get("player_name", "")
        platform = request.POST.get("platform", "")
        try:
            player = await sync_to_async(Player.objects.get)(name=player_name, platform=platform)
            exists = True
        except Player.DoesNotExist:
            player = Player.create(player_name, platform)
        except Player.MultipleObjectsReturned:
            player = await Player.objects.all().afilter(name=player_name, platform=platform).afirst()
        finally:
            if not exists:
                try:
                    player_data = await api_update_helper.ApiUpdateHelper.get_player_data(
                        player
                    )  # Change this to allow for testing.
                    player.avatar_id = player_data["profileIconId"]
                    exists = True
                except Exception:
                    exists = False

        return render(request, "tracker/partials/user_validation.html", context=locals())


@require_http_methods(["GET", "POST"])
def challenge(request, challenge_id=0):
    if request.htmx and challenge_id == 0:
        challenge_id = request.POST.get("search_input", None)
        return HttpResponseClientRedirect(reverse("challenge") + "{0}/".format(challenge_id))  # FIXME: Janky as fuck
    try:
        challenge_data = Challenge.objects.filter(id=challenge_id).first()
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
    except Challenge.DoesNotExist:
        messages.error(request, "404")
        return redirect(reverse("error"))
    except Exception:
        messages.error(request, "400")
        return redirect(reverse("error"))
    return render(request, "tracker/challenge.html", context=locals())


@cache_page(60 * 15)
@require_GET
def search(request):
    return render(request, "tracker/partials/search_modal.html")


def challenge_loading(request, job_id):
    queue = get_queue("high")
    job = queue.fetch_job(job_id)
    if job.is_finished:
        challenge_id = job.result
        return redirect("challenge", challenge_id=challenge_id)
    return render(request, "tracker/challenge_loading.html", context=locals())
