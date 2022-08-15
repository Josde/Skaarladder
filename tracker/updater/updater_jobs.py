import asyncio
from datetime import timedelta
import traceback

import aiohttp
from asgiref.sync import sync_to_async
from django_rq import get_queue
from rq.job import Dependency
from sentry_sdk import capture_message

from SoloQTracker.settings import BASE_DIR
import tracker.utils.constants as constants
from tracker.models import Ladder, Ladder_Player, Player
from tracker.updater.user_updater import update


def enqueue_periodic():
    """
    Helper function to enqueue the periodic update after all jobs have been completed.
    This only exists because rq enqueue_in takes the time when it is called, rather than when dependencies are finished.
    Therefore, to enqueue a job X minutes after its dependencies complete, we have to use a complementary job.
    This could probably be turned into a generic function that takes the function to enqueue but I'm too lazy for it right now.
    """
    queue = get_queue()
    queue.enqueue_in(time_delta=timedelta(minutes=constants.UPDATE_DELAY), func=periodic_update)


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
    await sync_to_async(queue.enqueue)(enqueue_periodic, depends_on=dependency)


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


# TODO: Maybe move these two functions below to a file in utils.


async def check_releases():
    if constants.RELEASE_CHECK:
        print("Checking if new releases exist...")
        URL = "https://api.github.com/repos/{0}/{1}/releases/latest".format(
            constants.RELEASE_USER, constants.RELEASE_REPO
        )
        try:
            current_release = await get_current_release()
            async with aiohttp.ClientSession() as session:
                async with session.get(URL) as response:
                    content = await response.json()
                    new_release = content["tag_name"]
            if current_release != new_release:
                RELEASE_URL = "https://github.com/{0}/{1}/releases/latest".format(
                    constants.RELEASE_USER, constants.RELEASE_REPO
                )
                message = """New version found. You are running {0} and {1} is available in GitHub.
                Go to {2} to download the newest version.""".format(
                    current_release, new_release, RELEASE_URL
                )
                print(message)
                capture_message(message, level="warning")
            else:
                print("No updates found!")
        except Exception:
            traceback.print_exc()
        queue = get_queue("low")
        queue.enqueue_in(time_delta=timedelta(minutes=constants.RELEASE_CHECK_DELAY), func=check_releases)


@sync_to_async
def get_current_release():
    file_path = BASE_DIR / "RELEASE"

    with open(file_path) as f:
        content = f.readline()
        clean_content = content.strip()

    return clean_content
