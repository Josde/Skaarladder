from . import abstract_update_helper


class TestUpdateHelper(abstract_update_helper.AbstractUpdateHelper):
    def __init__(
        self,
        player_content=None,
        ranked_content=None,
        streak_content=None,
        match_history_details_content=None,
        result_content=None,
    ):
        super().__init__()
        self.player_content = player_content
        self.ranked_content = ranked_content
        self.streak_content = streak_content
        self.match_history_details_content = match_history_details_content
        self.result_content = result_content

    async def get_player_data(self, player):
        return self.player_content

    async def get_player_ranked_data(self, player):
        return self.streak_content

    async def get_streak_data(self, player):
        return self.match_history_content

    async def get_match_history_details(self, player, count, queue):
        return self.match_history_details_content

    async def get_match_result(self, player, match_data):
        return self.result_content
