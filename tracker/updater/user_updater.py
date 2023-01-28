import traceback
from typing import List, Optional

from asgiref.sync import sync_to_async
from django.utils import timezone
import sentry_sdk
from pyot.core.exceptions import NotFound

from tracker.models import Ladder_Player, Player
from tracker.updater import api_update_helper, test_update_helper, abstract_update_helper
from tracker.utils.league import rank_to_lp
from tracker.utils.misc import update_fields
from tracker.utils import constants


# We did queries outside of the helper functions to make it more testable.
async def update(player_name: str, is_first_run: bool = False, test: bool = False):
    """Function that takes a player name and updates all of its information in the DB
    Args:
        player_name (str): The name of the player to update.
        is_first_run (bool, optional): Whether this is the first time the player is updated or not.
                                        Setting it to True makes it so it always updates everything. Defaults to False.
        test (bool, optional): Currently unused. Makes the backend be a TestUpdateHelper (kind of unimplemented rn). Defaults to False.
    """
    # Prettify this function.
    previous_absolute_lp = 0
    queried_player = await Player.objects.all().aget(name=player_name)
    if test:
        backend = test_update_helper.TestUpdateHelper()
    else:
        backend = api_update_helper.ApiUpdateHelper()
    time_since_last_update = timezone.now() - queried_player.last_data_update

    previous_absolute_lp = queried_player.absolute_lp
    if not queried_player.puuid or int(time_since_last_update.total_seconds()) // 3600 >= constants.PLAYER_DATA_UPDATE_DELAY:
        # timedelta has no minutes attribute for some reason?? lmfao bdfl wtf
        # Parse user data (name, id, profile pic...)
        try:
            await update_player_data(queried_player, backend)
        except Exception:
            pass
    if not queried_player.puuid:  # invalid player
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
        print(
            f"[{player_name} PlayerUpdater] Player has the same LP as last time, skipping ladder and streak updates..."
        )
        await sync_to_async(queried_player.save)()


async def update_player_data(queried_player: Player, backend: abstract_update_helper) -> Optional[dict]:
    """Updates the general data of a summoner (name, IDs, icon...)

    Args:
        queried_player (Player): The player that will be queried. It's fields will be updated when this function is called.
        backend (abstract_update_helper): The backend to use for getting the data. Must be a class that implements abstract_update_helper.

    Returns:
        Optional[dict]: The new player data. Unused, but returns something to keep the pattern from this file.
    """
    player_data = None
    try:
        player_data = await backend.get_player_data(queried_player)
        player_data["last_data_update"] = timezone.now()
        await sync_to_async(update_fields)(
            queried_player,
            player_data,
            {
                "name": "name",
                "puuid": "puuid",
                "id": "summoner_id",
                "accountId": "account_id",
                "profileIconId": "avatar_id",
                "last_data_update": "last_data_update",
            },
        )
    except NotFound:  # TODO: This makes the code more coupled, should look into another way of catching this exact exception.
        print(f"Player {queried_player.name} could not be found.")
    except Exception as err:
        sentry_sdk.capture_exception(err)
        traceback.print_exc()
    return player_data


async def update_ranked_data(queried_player: Player, backend: abstract_update_helper) -> int:
    """Updates the ranked data of the player. That is, it's LP, it's rank, wins and losses...

    Args:
        queried_player (Player): The player that will be queried. It's fields will be updated when this function is called.
        backend (abstract_update_helper): The backend to use for getting the data. Must be a class that implements abstract_update_helper.

    Returns:
        int: The current LP of the player, or 0. Used for logic inside the update() function.
    """
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
            current_absolute_lp = 0
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
            

        await sync_to_async(update_fields)(queried_player, complete_ranked_data)
        return current_absolute_lp
    except Exception as err:
        sentry_sdk.capture_exception(err)
        traceback.print_exc()
        return 0


async def update_streak_data(queried_player: Player, backend: abstract_update_helper) -> int:
    """Gets wether the player is on a winstreak or lose streak.

    Args:
        queried_player (Player): The player that will be queried. It's fields will be updated when this function is called.
        backend (abstract_update_helper): The backend to use for getting the data. Must be a class that implements abstract_update_helper.

    Returns:
        int: The streak or 0 if error. It's a number representing how many wins or losses (if it is negative) the player has had in a row.
    """
    try:
        streak = await backend.get_streak_data(queried_player)
        queried_player.streak = streak
    except Exception as err:
        sentry_sdk.capture_exception(err)
        traceback.print_exc()
        return 0
    return streak


async def update_player_ladder_data(
    queried_player: Player, ladders: List[Ladder_Player], current_absolute_lp: int
) -> List[Ladder_Player]:
    """Updates all the ladders this player is in with it's new information

    Args:
        queried_player (Player): The player data.
        ladders (List[Ladder_Player]): A list of ladders that this player is in.
        current_absolute_lp (int): The difference of LP between the player and Iron IV 0LP. Used for some logic.

    Returns:
        List[Ladder_Player]: The new list. Used to update the ladders outside of the function with a query.
    """
    async for item in ladders:
        ladder_details = item.ladder_id
        now = timezone.now()
        if ladder_details.end_date <= now or ladder_details.start_date >= now:
            print(
                f"[{queried_player.name} Updater] Found challenge {ladder_details.id} that hasn't started or already ended, skipping."
            )
            continue
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
