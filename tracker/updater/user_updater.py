import asyncio
import re
from django.utils import timezone
from tracker.utils.league import rank_to_lp
from tracker.models import Player, Challenge_Player
import traceback

from asgiref.sync import sync_to_async
from tracker.updater import api_update_helper, test_update_helper


async def update(player_name, test=False):
    """Function that gets the updated data for a user and returns it."""
    DEBUG = True
    current_absolute_lp = previous_absolute_lp = 0
    queried_player = await sync_to_async(Player.objects.all().get)(name=player_name)
    if test:
        backend = test_update_helper.TestUpdateHelper()
    else:
        backend = api_update_helper.ApiUpdateHelper()
    time_since_last_update = timezone.now() - queried_player.last_data_update

    previous_absolute_lp = rank_to_lp(
        queried_player.tier,
        queried_player.rank,
        queried_player.lp,
    )
    if queried_player.puuid == "" or time_since_last_update.days >= 7 or DEBUG:
        # Parse user data )name, id, profile pic...)
        try:
            await update_player_data(queried_player, backend)
        except Exception:  # same as below
            return
    if queried_player.puuid == "":  # invalid player
        return
    # Create tasks, since we can do everything else asynchronously
    current_absolute_lp = await update_ranked_data(queried_player, backend)
    await queried_player.asave()
    if previous_absolute_lp != current_absolute_lp or queried_player.tier == "UNRANKED":
        # TODO: Change the unranked part to be a "first time" thing instead.
        challenges = await update_player_challenge_data(queried_player, current_absolute_lp)
        await Challenge_Player.objects.abulk_update(challenges, ["progress", "progress_delta"])


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

    except Exception:
        traceback.print_exc()


async def update_ranked_data(queried_player, backend):
    tasks = [
        backend.get_player_ranked_data(queried_player),
        backend.get_streak_data(queried_player),
    ]
    try:
        ranked_data, streak = await asyncio.gather(*tasks)
        current_absolute_lp = 0
        if ranked_data is not None:
            complete_ranked_data = {
                "streak": streak,
                "wins": ranked_data["wins"],
                "losses": ranked_data["losses"],
                "winrate": 100 * ranked_data["wins"] / (ranked_data["wins"] + ranked_data["losses"]),
                "tier": ranked_data["tier"],
                "rank": ranked_data["rank"],
                "lp": ranked_data["leaguePoints"],
                "last_ranked_update": timezone.now(),
            }

            current_absolute_lp = rank_to_lp(
                queried_player.tier,
                queried_player.rank,
                queried_player.lp,
            )
        else:
            complete_ranked_data = {
                "streak": 0,
                "wins": 0,
                "losses": 0,
                "winrate": 0,
                "tier": "UNRANKED",
                "rank": "NONE",
                "lp": 0,
                "last_ranked_update": timezone.now(),
            }
            current_absolute_lp = 0

        await sync_to_async(update_fields)(
            queried_player, complete_ranked_data, dict([tuple([x, x]) for x in complete_ranked_data.keys()])
        )
        return current_absolute_lp
    except Exception:  # For debugging, implement errors later.
        traceback.print_exc()
        return None


async def update_player_challenge_data(queried_player, current_absolute_lp):
    # TODO: Move queries out of these functions?
    challenges = Challenge_Player.objects.filter(player_id=queried_player.id).select_related("challenge_id").all()

    async for item in challenges:
        challenge_details = item.challenge_id
        previous_progress = item.progress
        if queried_player.tier == "UNRANKED":
            item.starting_tier = "UNRANKED"
            item.starting_rank = "NONE"
        else:
            if challenge_details.is_absolute:
                absolute_starting_lp = 0
            elif item.starting_tier == "UNRANKED" or item.starting_rank == "NONE":
                absolute_starting_lp = 0
                item.starting_tier = queried_player.tier
                item.starting_rank = queried_player.rank
            else:
                absolute_starting_lp = rank_to_lp(item.starting_tier, item.starting_rank, item.starting_lp)
            item.progress = current_absolute_lp - absolute_starting_lp
            item.progress_delta = item.progress - previous_progress
    return challenges
