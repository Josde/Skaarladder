import asyncio
from django.utils import timezone
from tracker.utils.league import rank_to_lp
from tracker.models import Player, Challenge_Player
import traceback

from asgiref.sync import sync_to_async
from tracker.updater import api_update_helper, test_update_helper


class UserUpdater:
    """Class that will take a Player as argument and will make the appropiate calls to return updated values for that user (helper functions) or update and commit it (update)."""

    # TODO: Make all of these, except backend, local variables and use dependency injection to make this testable.
    queried_player = None
    player_data = None
    ranked_data = None
    streak_data = None
    current_absolute_lp = 0
    previous_absolute_lp = 0
    backend = None

    def __init__(self, player: Player, test=False):
        self.queried_player = player
        if test:
            self.backend = test_update_helper.TestUpdateHelper()  # TPDP: Pass content here
        else:
            self.backend = api_update_helper.ApiUpdateHelper()

    async def update(self):
        """Function that gets the updated data for a user and returns it."""
        DEBUG = True
        time_since_last_update = timezone.now() - self.queried_player.last_data_update
        try:
            # TODO: Make rank_to_lp fail silently so I don't have to use try/except here?
            self.previous_absolute_lp = rank_to_lp(
                self.queried_player.tier,
                self.queried_player.rank,
                self.queried_player.lp,
            )
        except Exception:
            self.previous_absolute_lp = 0
        if self.queried_player.puuid == "" or time_since_last_update.days >= 7 or DEBUG:
            # Parse user data )name, id, profile pic...)
            await self.update_player_data()
            # Create tasks, since we can do everything else asynchronously
        await self.update_ranked_data()
        await sync_to_async(self.queried_player.save)()
        if self.previous_absolute_lp != self.current_absolute_lp or self.queried_player.tier == "UNRANKED":
            # TODO: Change the unranked part to be a "first time" thing instead.
            await self.update_player_challenge_data()

    def update_fields(self, obj, data_dict: dict, data_to_obj_fields: dict):
        for field in data_to_obj_fields.keys():
            if field in data_dict.keys() and hasattr(obj, data_to_obj_fields[field]):
                setattr(obj, data_to_obj_fields[field], data_dict[field])
            else:
                print("Couldn't find dict field {0} or object field {1}", field, data_to_obj_fields[field])
                raise KeyError

    async def update_player_data(self):
        try:
            self.player_data = await self.backend.get_player_data(self.queried_player)
            await sync_to_async(self.update_fields)(
                self.queried_player,
                self.player_data,
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

    async def update_ranked_data(self):
        tasks = [
            self.backend.get_player_ranked_data(self.queried_player),
            self.backend.get_streak_data(self.queried_player),
        ]
        try:
            self.ranked_data, self.streak = await asyncio.gather(*tasks)
            current_absolute_lp = 0
            if self.ranked_data is not None:
                complete_ranked_data = {
                    "streak": self.streak,
                    "wins": self.ranked_data["wins"],
                    "losses": self.ranked_data["losses"],
                    "winrate": 100
                    * self.ranked_data["wins"]
                    / (self.ranked_data["wins"] + self.ranked_data["losses"]),
                    "tier": self.ranked_data["tier"],
                    "rank": self.ranked_data["rank"],
                    "lp": self.ranked_data["leaguePoints"],
                    "last_ranked_update": timezone.now(),
                }

                self.current_absolute_lp = rank_to_lp(
                    self.queried_player.tier,
                    self.queried_player.rank,
                    self.queried_player.lp,
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
                self.current_absolute_lp = 0

            await sync_to_async(self.update_fields)(
                self.queried_player, complete_ranked_data, dict([tuple([x, x]) for x in complete_ranked_data.keys()])
            )
        except Exception:  # For debugging, implement errors later.
            traceback.print_exc()

    async def update_player_challenge_data(self):
        # TODO: Move queries out of these functions?
        challenges = await sync_to_async(list)(
            Challenge_Player.objects.filter(player_id=self.queried_player.id).select_related("challenge_id").all()
        )
        for item in challenges:
            challenge_details = item.challenge_id
            previous_progress = item.progress
            if self.queried_player.tier == "UNRANKED":
                item.starting_tier = "UNRANKED"
                item.starting_rank = "NONE"
            else:
                if challenge_details.is_absolute:
                    self.absolute_starting_lp = 0
                elif item.starting_tier == "UNRANKED" or item.starting_rank == "NONE":
                    self.absolute_starting_lp = 0
                    item.starting_tier = self.queried_player.tier
                    item.starting_rank = self.queried_player.rank
                else:
                    self.absolute_starting_lp = rank_to_lp(item.starting_tier, item.starting_rank, item.starting_lp)
                item.progress = self.current_absolute_lp - self.absolute_starting_lp
                item.progress_delta = item.progress - previous_progress
        # TODO: Change this to abulk_update once it gets to Django release
        # await sync_to_async(Challenge_Player.objects.bulk_update(challenges, ['progress', 'progress_delta']))
        await sync_to_async(Challenge_Player.objects.bulk_update)(challenges, ["progress", "progress_delta"])
