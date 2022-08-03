from abc import ABC, abstractclassmethod


class AbstractUpdateHelper(ABC):
    @abstractclassmethod
    async def get_player_data(self, player):
        pass

    @abstractclassmethod
    async def get_player_ranked_data(self, player):
        pass

    @abstractclassmethod
    async def get_streak_data(self, player):
        pass

    @abstractclassmethod
    async def get_match_history_details(self, player, count, queue):
        pass

    @abstractclassmethod
    async def get_match_result(self, player, match_data):
        pass
