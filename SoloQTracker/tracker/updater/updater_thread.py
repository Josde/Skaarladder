import threading
from tracker.models import Player
from .update_helper import UpdateHelper
import asyncio
import tracker.utils.constants as constants
from asgiref.sync import sync_to_async
class UpdaterThread(threading.Thread):
    """ Class that manages a background task for updating user data periodically """    

    
    def run(self):
        asyncio.run(self.main_loop())
        
    async def main_loop(self):
        while True:
            tasks = await sync_to_async(self.build_task_list)()
            # FIXME: For some reason this causes rate limiting
            #await asyncio.gather(*tasks)
            for item in tasks:
                await item
                await asyncio.sleep(0.5)
            await asyncio.sleep(constants.UPDATE_DELAY)
        
    def build_task_list(self):
        task_list = []
        for player in Player.objects.all():
            uh = UpdateHelper(player)
            task_list.append(uh.update())
        return task_list