from tracker.updater.abstract_update_helper import AbstractUpdateHelper
class ApiUpdateHelper(AbstractUpdateHelper):
    async def get_player_data(self, player):
        print(
            "[{0} UserUpdater] Running player data update, either this is the first update or last update was over 7 days ago (lu: {1})".format(
                player.name, player.last_data_update
            )
        )
        """ Updates the ID, name and such of our Player class.
        Only ran if it's the first time the player has been queried or if last update was a while ago. """
        res = await lol.Summoner(name=player.name, platform=player.platform).get()
        return res.dict()

    async def get_player_ranked_data(self, player):
        """Queries the player's SoloQ data, getting stats such as LP, winrate and etc."""
        print("[{0} UserUpdater] Running SoloQ data update.".format(player.name))
        queue_data = await lol.SummonerLeague(player.summoner_id, platform=player.platform).get()
        soloq_dict = None
        for item in queue_data.entries:
            soloq_dict = item.dict()
            if soloq_dict is not None and soloq_dict["queueType"] == "RANKED_SOLO_5x5":  # Fiter SoloQ
                break
        return soloq_dict

    async def get_streak_data(self, player):
        """Queries the player's match history and processes his win or loss streak."""
        print("[{0} UserUpdater] Running streak data update".format(player.name))
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
