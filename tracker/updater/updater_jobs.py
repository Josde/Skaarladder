import threading
from tracker.models import Player, Ladder, Ladder_Player
import asyncio
import tracker.utils.constants as constants
from asgiref.sync import sync_to_async
from tracker.updater.user_updater import update
from datetime import datetime, timedelta
from django_rq import get_queue
from rq.job import Dependency


async def periodic_update():
    player_query = Player.objects.all().only("name")
    queue = await sync_to_async(get_queue)()
    jobs = []
    async for player in player_query:
        jobs.append(queue.prepare_data(update, [player.name]))
    with queue.connection.pipeline() as pipe:
        enqueued_jobs = await sync_to_async(queue.enqueue_many)(jobs, pipeline=pipe)
        await sync_to_async(pipe.execute)()
    dependency = Dependency(jobs=enqueued_jobs)
    await sync_to_async(queue.enqueue_in)(
        timedelta(seconds=constants.UPDATE_DELAY), periodic_update, depends_on=dependency
    )


def create_ladder_job(name, start_date, end_date, player_platform, is_absolute, ignore_unranked):
    ladder = Ladder(
        name=name,
        start_date=start_date,
        end_date=end_date,
        is_absolute=is_absolute,
        ignore_unranked=ignore_unranked,
    )
    ladder.save()
    tasks = []
    players = []
    player_ladders = []
    for item in player_platform:
        print("Searching player {0} {1}".format(item[0], item[1]))
        try:
            player = Player.objects.get(name=item[0], platform=item[1])
        except Player.DoesNotExist:
            player = Player.create(name=item[0], platform=item[1])
            player.save()
            players.append(player)  # We only created non existing players to prevent violating PK uniqueness
            tasks.append(update(player, is_first_run=True))  # Only update if not in DB
        except Player.MultipleObjectsReturned:
            query = Player.objects.all().filter(name=item[0], platform=item[1])
            player = query[0]
        finally:
            player_ladder = Ladder_Player(
                player_id=player,
                ladder_id=ladder,
                starting_lp=0,
                starting_tier="UNRANKED",
                starting_rank="NONE",
            )
            player_ladders.append(player_ladder)
    for item in player_ladders:
        item.save()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))

    return ladder.id
