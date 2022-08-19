from abc import ABC, abstractmethod


class AbstractUpdateHelper(ABC):
    @abstractmethod
    async def get_player_data(self, player):
        pass

    @abstractmethod
    async def get_player_ranked_data(self, player):
        pass

    @abstractmethod
    async def get_streak_data(self, player):
        pass

    @abstractmethod
    async def get_match_history_details(self, player, count, queue):
        pass

    @abstractmethod
    async def get_match_result(self, player, match_data):
        pass
