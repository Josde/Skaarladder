import asyncio
from django.utils import timezone
from tracker.utils.league import rankToLP
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
            previous_absolute_lp = rankToLP(
                self.queried_player.tier,
                self.queried_player.rank,
                self.queried_player.lp,
            )
        except Exception:
            previous_absolute_lp = 0
        if self.queried_player.puuid == "" or time_since_last_update.days >= 7 or DEBUG:
            try:
                self.player_data = await self.get_player_data()
                self.queried_player.name = self.player_data["name"]
                self.queried_player.puuid = self.player_data["puuid"]
                self.queried_player.summoner_id = self.player_data["id"]
                self.queried_player.account_id = self.player_data["accountId"]
                self.queried_player.avatar_id = self.player_data["profileIconId"]
                await sync_to_async(self.queried_player.save)()

            except Exception:
                traceback.print_exc()
        # Create tasks, since we can do everything else asynchronously
        tasks = [self.get_player_ranked_data(), self.get_streak_data()]
        try:
            self.ranked_data, self.streak = await asyncio.gather(*tasks)
            current_absolute_lp = 0
            if self.ranked_data is not None:
                self.queried_player.streak = self.streak
                self.queried_player.wins = self.ranked_data["wins"]
                self.queried_player.losses = self.ranked_data["losses"]
                self.queried_player.winrate = (
                    100 * self.queried_player.wins / (self.queried_player.wins + self.queried_player.losses)
                )
                self.queried_player.tier = self.ranked_data["tier"]
                self.queried_player.rank = self.ranked_data["rank"]
                self.queried_player.lp = self.ranked_data["leaguePoints"]
                self.queried_player.last_ranked_update = timezone.now()

                current_absolute_lp = rankToLP(
                    self.queried_player.tier,
                    self.queried_player.rank,
                    self.queried_player.lp,
                )
            else:
                self.queried_player.streak = (
                    self.queried_player.wins
                ) = self.queried_player.losses = self.queried_player.winrate = 0
                self.queried_player.tier = "UNRANKED"
                self.queried_player.rank = "NONE"
                self.queried_player.lp = 0
                self.queried_player.last_ranked_update = timezone.now()

            if (
                previous_absolute_lp != current_absolute_lp or self.queried_player.tier == "UNRANKED"
            ):  # FIXME: Change the unranked part to be better
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
                            item.starting_tier = self.queried_player.tier
                            item.starting_rank = self.queried_player.rank
                            absolute_starting_lp = rankToLP(
                                self.queried_player.tier,
                                self.queried_player.rank,
                                self.queried_player.lp,
                            )
                        item.progress = current_absolute_lp - absolute_starting_lp
                        item.progress_delta = item.progress - previous_progress
                # TODO: Change this to abulk_update once it gets to Django release
                # await sync_to_async(Challenge_Player.objects.bulk_update(challenges, ['progress', 'progress_delta']))
                await sync_to_async(Challenge_Player.objects.bulk_update)(challenges, ["progress", "progress_delta"])
            await sync_to_async(self.queried_player.save)()
        except Exception:  # For debugging, implement errors later.
            traceback.print_exc()

    async def get_player_data(self):
        print(
            "[{0} UpdateHelper] Running player data update, either this is the first update or last update was over 7 days ago (lu: {1})".format(
                self.queried_player.name, self.queried_player.last_data_update
            )
        )
        """ Updates the ID, name and such of our Player class.
        Only ran if it's the first time the player has been queried or if last update was a while ago. """
        res = await lol.Summoner(name=self.queried_player.name, platform=self.queried_player.platform).get()
        return res.dict()

    async def get_player_ranked_data(self):
        """Queries the player's SoloQ data, getting stats such as LP, winrate and etc."""
        print("[{0} UpdateHelper] Running SoloQ data update.".format(self.queried_player.name))
        queue_data = await lol.SummonerLeague(
            self.queried_player.summoner_id, platform=self.queried_player.platform
        ).get()
        soloq_keys = [
            "queueType",
            "tier",
            "rank",
            "leaguePoints",
            "wins",
            "losses",
        ]  # Partes de los datos que nos interesan, por simplificar
        soloq_dict = None
        for item in queue_data.entries:
            soloq_dict = item.dict()
            if soloq_dict is not None and soloq_dict["queueType"] == "RANKED_SOLO_5x5":  # Fiter SoloQ
                break
        return soloq_dict

    async def get_streak_data(self):
        """Queries the player's match history and processes his win or loss streak."""
        print("[{0} UpdateHelper] Running streak data update".format(self.queried_player.name))
        tasks = []
        matches = []
        result = last_result = None
        streak = 0
        history = (
            await lol.MatchHistory(self.queried_player.puuid, region=self.queried_player.region)
            .query(count=10, queue=420)
            .get()
        )
        for match in history.matches:
            tasks.append(match.get())

        matches = await asyncio.gather(*tasks)

        for match_data in matches:
            if (result != last_result) and last_result is not None:
                break
            teams = match_data.info.teams
            for t in teams:
                participant_ids = [p.puuid for p in t.participants]
                if self.queried_player.puuid in participant_ids:
                    if t.win == result or result is None:
                        if t.win:
                            streak += 1
                        else:
                            streak -= 1
                    last_result = result
                    result = t.win
        return streak
