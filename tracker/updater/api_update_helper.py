import asyncio
from typing import List

from pyot.models import lol

from . import abstract_update_helper
from tracker.models import Player
from tracker.utils import constants


class ApiUpdateHelper(abstract_update_helper.AbstractUpdateHelper):
    async def get_player_data(self, player: Player) -> dict:
        """Queries the API for the Summoner Data (name, IDs...)

        Args:
            player (Player): The player that will be queried

        Returns:
            dict: A dict containing the player data
        """
        print(f"[{player.name} UserUpdater] Running player data update.")
        res = await lol.Summoner(name=player.name, platform=player.platform).get()
        return res.dict()

    async def get_player_ranked_data(self, player: Player) -> dict:
        """Gets the ranked data for SoloQ. This data contains wins, losses, LP...

        Args:
            player (Player): The player that will be queried

        Returns:
            dict: A dict containing the ranked data
        """
        print(f"[{player.name} UserUpdater] Running SoloQ data update.")
        queue_data = await lol.SummonerLeague(player.summoner_id, platform=player.platform).get()
        soloq_dict = None
        for item in queue_data.entries:
            soloq_dict = item.dict()
            if soloq_dict is not None and soloq_dict["queueType"] == "RANKED_SOLO_5x5":  # Fiter SoloQ
                break
        return soloq_dict

    async def get_streak_data(self, player: Player) -> int:
        """Gets the win or lose streak of a player.

        Args:
            player (Player): The player that will be queried

        Returns:
            int: The amount of wins (positive) or losses (negative) the player has had in a row.
        """
        print(f"[{player.name} UserUpdater] Running streak data update")
        matches = []
        result = last_result = None
        streak = 0

        matches = await self.get_match_history_details(player, count=constants.MAX_STREAK_LENGTH, queue=420)

        for match_data in matches:
            if (result != last_result) and last_result is not None:
                break
            won = await self.get_match_result(player, match_data)
            last_result = result
            result = won
            if result == last_result:
                streak += 1 if won else -1

        return streak

    async def get_match_history_details(self, player: Player, count: int, queue: int) -> List[lol.Match]:
        """Gets N amount of matches from a player's match history.

        Args:
            player (Player): The player whose matches will be queried
            count (int): How many matches to query
            queue (int): Which queue to query (420 = SoloQ, 440 = Flex). Check https://static.developer.riotgames.com/docs/lol/queues.json for other gamemodes.

        Returns:
            List[lol.Match]: A list of matches.
        """
        tasks = []
        history = await lol.MatchHistory(player.puuid, region=player.region).query(count=count, queue=queue).get()

        for match in history.matches:
            tasks.append(match.get())

        return await asyncio.gather(*tasks)

    async def get_match_result(self, player: Player, match_data: lol.Match) -> bool:
        """Gets the result (win or loss) of a match

        Args:
            player (Player): The player whose result we want to know. We need this to identify his team.
            match_data (lol.Match): The match to parse.

        Returns:
            bool: True if won, False if lost.
        """
        teams = match_data.info.teams
        for team in teams:
            participant_ids = [p.puuid for p in team.participants]
            if player.puuid in participant_ids:  # Check the result for the team in which the player is in.
                return team.win
