import threading
from tracker.models import Player
from tracker.updater.user_updater import UserUpdater
import asyncio
import tracker.utils.constants as constants
from asgiref.sync import sync_to_async
from tracker.updater.user_updater import UserUpdater


class UpdaterThread(threading.Thread):
    """Class that manages a background task for updating user data periodically"""

    # FIXME: Use schedule and a polled sleep to make this way easier, and make it support tasks.
    # https://github.com/dbader/schedule

    def run(self):
        asyncio.run(self.main_loop())

    async def main_loop(self):
        while True:
            tasks = await sync_to_async(self.build_task_list)()
            # FIXME: For some reason this causes rate limiting
            # await asyncio.gather(*tasks)
            for item in tasks:
                await item
                await asyncio.sleep(0.5)
            await asyncio.sleep(constants.UPDATE_DELAY)

    def build_task_list(self):
        task_list = []
        for player in Player.objects.all():
            uu = UserUpdater(player)
            task_list.append(uu.update())
        return task_list
