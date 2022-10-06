import traceback
import uuid
from datetime import datetime

from asgiref.sync import sync_to_async
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET, require_http_methods
from django_htmx.http import HttpResponseClientRedirect
from django_rq import get_queue

from tracker.updater import api_update_helper

from .forms import LadderForm, PlayerForm
from .models import Ladder, Ladder_Player, Player
from .tables import LadderTable
from .updater import updater_jobs


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


async def create_ladder(request):
    """View that represents the ladder creation form and it's logic."""
    if request.method == "POST":
        print(request.POST)
        submitted_form = LadderForm(request.POST)
        player_forms = []
        valid_player_forms = True
        _player_platform = list(
            zip(
                request.POST.getlist("player_name"),
                request.POST.getlist("platform"),
                request.POST.getlist("initial-valid"),
            )
        )
        for item in _player_platform:
            player_form = PlayerForm(
                form_id=uuid.uuid4(), initial={"player_name": item[0], "platform": item[1], "valid": item[2]}
            )
            player_form.data["player_name"] = item[0]
            player_form.data["platform"] = item[1]
            player_form.data["valid"] = item[2]
            player_forms.append(player_form)
        if len(player_forms) < 2:
            submitted_form.add_error(error="Must have at least 2 players in your ladder.")
        if not submitted_form.is_valid() or not valid_player_forms:
            return render(request, "tracker/ladder_form.html", {"form": submitted_form, "player_forms": player_forms})

        _name = request.POST["name"]
        _start_date = datetime.strptime(request.POST["start_date"], "%Y-%m-%dT%H:%M")
        _end_date = datetime.strptime(request.POST["end_date"], "%Y-%m-%dT%H:%M")

        _is_absolute = "is_absolute" in request.POST.keys()
        _ignore_unranked = "ignore_unranked" in request.POST.keys()
        # if ()
        queue = get_queue("high")
        job = queue.enqueue(
            updater_jobs.create_ladder_job,
            kwargs={
                "name": _name,
                "start_date": _start_date,
                "end_date": _end_date,
                "player_platform": _player_platform,
                "is_absolute": _is_absolute,
                "ignore_unranked": _ignore_unranked,
            },
        )
        return redirect("ladder_loading", job_id=job.id)
    else:
        form = LadderForm()
        return render(request, "tracker/ladder_form.html", {"form": form})


@require_GET
def create_user_form(request):
    """View that spawns a PlayerForm with a certain UUID. Used in conjunction with HTMX to dynamically add forms."""
    form_id = uuid.uuid4()
    form = PlayerForm(form_id=form_id)

    return render(request, "tracker/partials/user_form.html", context=locals())


async def provisional_parse(request):
    """View that gives out wether a player exists or not. Used with HTMX to dynamically add this below an user form."""
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
                    api = api_update_helper.ApiUpdateHelper()
                    player_data = await api.get_player_data(player)  # Change this to allow for testing.
                    player.avatar_id = player_data["profileIconId"]
                    exists = True
                except Exception:
                    exists = False

        return render(request, "tracker/partials/user_validation.html", context=locals())


@require_http_methods(["GET", "POST"])
def ladder(request, ladder_id=0):
    """View that represents a ladder table."""
    # FIXME:  mccabe: MC0001 / ladder is too complex (11)
    if request.htmx and ladder_id == 0:
        # If the request is HTMX, it comes from search.
        ladder_id = request.POST.get("search_input", None)
        if not ladder_id:
            return HttpResponseClientRedirect(reverse("error"))
        return HttpResponseClientRedirect(reverse("ladder") + f"{ladder_id}/")  # FIXME: Janky as fuck
    # If request is not HTMX, we have to render a table.
    try:
        ladder_data = Ladder.objects.filter(id=ladder_id).first()
        if ladder_data.is_absolute:
            order = ("-player_id__absolute_lp")
        else:
            order = ("-progress", "-player_id__absolute_lp")
        if ladder_data.ignore_unranked:
            player_query = (
                Ladder_Player.objects.filter(ladder_id=ladder_id)
                .exclude(player_id__tier="UNRANKED")
                .exclude(ignored=True)
                .select_related("player_id")
                .order_by(order)
            )
        else:
            player_query = (
                Ladder_Player.objects.filter(ladder_id=ladder_id)
                .exclude(ignored=True)
                .select_related("player_id")
                .order_by(order)
            )
        table = LadderTable(player_query)
        if ladder_data.is_absolute:
            table.exclude = "progress"
        # These variables are for the template and passed through locals()
        right_now = timezone.now()
        start_date = ladder_data.start_date
        end_date = ladder_data.end_date
        ladder_name = ladder_data.name
        ladder_id = ladder_data.id
        if start_date <= right_now <= end_date:
            ladder_status = "Ongoing"
        elif right_now <= start_date:
            ladder_status = "Scheduled"
        else:
            ladder_status = "Done"
        print(f"Starts {start_date} ends {end_date} is {ladder_status}")
    except Ladder.DoesNotExist:
        messages.error(request, "404")
        traceback.print_exc()
        return redirect(reverse("error"))
    except Exception:
        messages.error(request, "400")
        traceback.print_exc()
        return redirect(reverse("error"))
    return render(request, "tracker/ladder.html", context=locals())


@require_GET
def search(request):
    """Renders the search template. Used with HTMX to dynamically add this on top of pages."""
    return render(request, "tracker/partials/search_modal.html")


@require_GET
def ladder_loading(request, job_id):
    """Temporal loading page while a Challenge is created. The template is reloaded every three seconds."""
    queue = get_queue("high")
    job = queue.fetch_job(job_id)

    if not job:
        messages.error(request, "404")
        return redirect(reverse("error"))

    if job.is_finished:
        ladder_id = job.result
        return redirect("ladder", ladder_id=ladder_id)
    return render(request, "tracker/ladder_loading.html", context=locals())
