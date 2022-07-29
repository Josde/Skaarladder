import asyncio
from django.utils import timezone
from tracker.utils.league import rank_to_lp
from tracker.models import Player, Challenge_Player, Challenge
import datetime
import traceback
from pyot.models import lol
from pyot.utils.lol.routing import platform_to_region
from asgiref.sync import sync_to_async


class UpdateHelper:
    """Class that will take a Player as argument and will make the appropiate calls to return updated values for that user (helper functions) or update and commit it (update)."""

    queried_player = None
    player_data = None
    ranked_data = None
    streak_data = None

    def __init__(self, player: Player):
        self.queried_player = player

    async def update(self):
        """Function that gets the updated data for a user and returns it."""
        DEBUG = True
        time_since_last_update = timezone.now() - self.queried_player.last_data_update
        try:
            previous_absolute_lp = rank_to_lp(
                self.queried_player.tier,
                self.queried_player.rank,
                self.queried_player.lp,
            )
        except Exception:
            previous_absolute_lp = 0
        if self.queried_player.puuid == "" or time_since_last_update.days >= 7 or DEBUG:
            try:
                self.player_data = await self.get_player_data(self.queried_player)
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
                await sync_to_async(self.queried_player.save)()

            except Exception:
                traceback.print_exc()
        # Create tasks, since we can do everything else asynchronously
        tasks = [self.get_player_ranked_data(self.queried_player), self.get_streak_data(self.queried_player)]
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

                current_absolute_lp = rank_to_lp(
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
                current_absolute_lp = 0

            await sync_to_async(self.update_fields)(
                self.queried_player, complete_ranked_data, dict([tuple([x, x]) for x in complete_ranked_data.keys()])
            )

            if previous_absolute_lp != current_absolute_lp or self.queried_player.tier == "UNRANKED":
                # FIXME: Change the unranked part to be better
                # Rank changed, must update all challenges
                challenges = await sync_to_async(list)(
                    Challenge_Player.objects.filter(player_id=self.queried_player.id)
                    .select_related("challenge_id")
                    .all()
                )
                for item in challenges:
                    challenge_details = item.challenge_id
                    previous_progress = item.progress
                    if self.queried_player.tier == "UNRANKED":
                        item.starting_tier = "UNRANKED"
                        item.starting_rank = "NONE"
                    else:
                        if challenge_details.is_absolute:
                            absolute_starting_lp = 0
                        elif item.starting_tier == "UNRANKED" or item.starting_rank == "NONE":
                            absolute_starting_lp = 0
                            item.starting_tier = self.queried_player.tier
                            item.starting_rank = self.queried_player.rank
                        else:
                            absolute_starting_lp = rank_to_lp(item.starting_tier, item.starting_rank, item.starting_lp)
                        item.progress = current_absolute_lp - absolute_starting_lp
                        item.progress_delta = item.progress - previous_progress
                # TODO: Change this to abulk_update once it gets to Django release
                # await sync_to_async(Challenge_Player.objects.bulk_update(challenges, ['progress', 'progress_delta']))
                await sync_to_async(Challenge_Player.objects.bulk_update)(challenges, ["progress", "progress_delta"])
            await sync_to_async(self.queried_player.save)()
        except Exception:  # For debugging, implement errors later.
            traceback.print_exc()

    async def get_player_data(self, player):
        print(
            "[{0} UpdateHelper] Running player data update, either this is the first update or last update was over 7 days ago (lu: {1})".format(
                player.name, player.last_data_update
            )
        )
        """ Updates the ID, name and such of our Player class.
        Only ran if it's the first time the player has been queried or if last update was a while ago. """
        res = await lol.Summoner(name=player.name, platform=player.platform).get()
        return res.dict()

    async def get_player_ranked_data(self, player):
        """Queries the player's SoloQ data, getting stats such as LP, winrate and etc."""
        print("[{0} UpdateHelper] Running SoloQ data update.".format(player.name))
        queue_data = await lol.SummonerLeague(player.summoner_id, platform=player.platform).get()
        soloq_dict = None
        for item in queue_data.entries:
            soloq_dict = item.dict()
            if soloq_dict is not None and soloq_dict["queueType"] == "RANKED_SOLO_5x5":  # Fiter SoloQ
                break
        return soloq_dict

    async def get_streak_data(self, player):
        """Queries the player's match history and processes his win or loss streak."""
        print("[{0} UpdateHelper] Running streak data update".format(player.name))
        matches = []
        result = last_result = None
        streak = 0

        matches = await self.get_match_history_details(player, count=10, queue=420)

        for match_data in matches:
            if (result != last_result) and last_result is not None:
                break
            won = await self.get_match_result(player, match_data)
            last_result = result
            result = won
            if result == last_result:
                streak += 1 if won else -1

        return streak

    async def get_match_history_details(self, player, count, queue):
        tasks = []
        history = await lol.MatchHistory(player.puuid, region=player.region).query(count=count, queue=queue).get()

        for match in history.matches:
            tasks.append(match.get())

        return await asyncio.gather(*tasks)

    async def get_match_result(self, player, match_data):
        teams = match_data.info.teams
        for t in teams:
            participant_ids = [p.puuid for p in t.participants]
            if player.puuid in participant_ids:
                if t.win:
                    return True
                else:
                    return False

    def update_fields(self, obj, data_dict: dict, data_to_obj_fields: dict):
        for field in data_to_obj_fields.keys():
            if field in data_dict.keys() and hasattr(obj, data_to_obj_fields[field]):
                setattr(obj, data_to_obj_fields[field], data_dict[field])
            else:
                print("Couldn't find dict field {0} or object field {1}", field, data_to_obj_fields[field])
                raise KeyError
