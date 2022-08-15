import traceback

from asgiref.sync import sync_to_async
from django.utils import timezone
import sentry_sdk

from tracker.models import Ladder, Ladder_Player, Player
from tracker.updater import api_update_helper, test_update_helper
from tracker.utils.league import rank_to_lp


async def update(player_name, is_first_run=False, test=False):
    """Function that gets the updated data for a user and returns it."""
    # Prettify this function.
    current_absolute_lp = previous_absolute_lp = 0
    queried_player = await Player.objects.all().aget(name=player_name)
    if test:
        backend = test_update_helper.TestUpdateHelper()
    else:
        backend = api_update_helper.ApiUpdateHelper()
    time_since_last_update = timezone.now() - queried_player.last_data_update

    previous_absolute_lp = queried_player.absolute_lp
    if queried_player.puuid == "" or time_since_last_update.days >= 3:
        # Parse user data (name, id, profile pic...)
        try:
            await update_player_data(queried_player, backend)
        except Exception:  # same as below
            return
    if queried_player.puuid == "":  # invalid player
        return
    # Create tasks, since we can do everything else asynchronously
    current_absolute_lp = await update_ranked_data(queried_player, backend)

    if (previous_absolute_lp != current_absolute_lp) or is_first_run:
        await update_streak_data(queried_player, backend)
        await sync_to_async(queried_player.save)()
        ladders = Ladder_Player.objects.filter(player_id=queried_player).select_related("ladder_id").all()
        ladders = await update_player_ladder_data(queried_player, ladders, current_absolute_lp)
        async for item in ladders:
            await sync_to_async(item.save)()
            # Ladder_Player.objects.abulk_update(ladders, ["progress", "progress_delta"]) doesn't work idk why
    else:
        await sync_to_async(queried_player.save)()


def update_fields(obj, data_dict: dict, data_to_obj_fields: dict):
    for field in data_to_obj_fields.keys():
        if field in data_dict.keys() and hasattr(obj, data_to_obj_fields[field]):
            setattr(obj, data_to_obj_fields[field], data_dict[field])
        else:
            print("Couldn't find dict field {0} or object field {1}", field, data_to_obj_fields[field])
            raise KeyError


async def update_player_data(queried_player, backend):
    try:
        player_data = await backend.get_player_data(queried_player)
        await sync_to_async(update_fields)(
            queried_player,
            player_data,
            {
                "name": "name",
                "puuid": "puuid",
                "id": "summoner_id",
                "accountId": "account_id",
                "profileIconId": "avatar_id",
            },
        )

    except Exception as err:
        sentry_sdk.capture_exception(err)
        traceback.print_exc()


async def update_ranked_data(queried_player, backend):
    try:
        ranked_data = await backend.get_player_ranked_data(queried_player)
        if ranked_data is not None:
            current_absolute_lp = rank_to_lp(
                ranked_data["tier"],
                ranked_data["rank"],
                ranked_data["leaguePoints"],
            )

            complete_ranked_data = {
                "wins": ranked_data["wins"],
                "losses": ranked_data["losses"],
                "winrate": 100 * ranked_data["wins"] / (ranked_data["wins"] + ranked_data["losses"]),
                "tier": ranked_data["tier"],
                "rank": ranked_data["rank"],
                "lp": ranked_data["leaguePoints"],
                "last_ranked_update": timezone.now(),
                "absolute_lp": current_absolute_lp,
            }

        else:
            complete_ranked_data = {
                "wins": 0,
                "losses": 0,
                "winrate": 0,
                "tier": "UNRANKED",
                "rank": "NONE",
                "lp": 0,
                "last_ranked_update": timezone.now(),
                "absolute_lp": 0,
            }
            current_absolute_lp = 0

        await sync_to_async(update_fields)(
            queried_player, complete_ranked_data, dict([tuple([x, x]) for x in complete_ranked_data.keys()])
        )
        return current_absolute_lp
    except Exception as err:
        sentry_sdk.capture_exception(err)
        traceback.print_exc()
        return 0


async def update_streak_data(queried_player, backend):
    try:
        streak = await backend.get_streak_data(queried_player)
        queried_player.streak = streak
    except Exception as err:
        sentry_sdk.capture_exception(err)
        traceback.print_exc()
        return 0
    return streak


async def update_player_ladder_data(queried_player, ladders, current_absolute_lp):
    async for item in ladders:
        ladder_details = item.ladder_id
        previous_progress = item.progress
        if queried_player.tier == "UNRANKED":
            item.starting_tier = "UNRANKED"
            item.starting_rank = "NONE"
        else:
            if ladder_details.is_absolute:
                absolute_starting_lp = 0
            elif item.starting_tier == "UNRANKED" or item.starting_rank == "NONE":
                absolute_starting_lp = 0
                item.starting_tier = queried_player.tier
                item.starting_rank = queried_player.rank
            else:
                absolute_starting_lp = rank_to_lp(item.starting_tier, item.starting_rank, item.starting_lp)
            item.progress = current_absolute_lp - absolute_starting_lp
            item.progress_delta = item.progress - previous_progress
    return ladders
