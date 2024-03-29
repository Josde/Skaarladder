import asyncio
from datetime import timedelta, datetime

from asgiref.sync import sync_to_async, async_to_sync
from django_rq import get_queue
from rq.job import Dependency

from SoloQTracker.settings import DEBUG
from tracker.utils import constants
from tracker.utils.misc import async_wrapper
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
    jobs = [x.func for x in queue.jobs]
    if periodic_update not in jobs and not DEBUG:
        print(f"[enqueue_periodic] Enqueuing new update in {constants.UPDATE_DELAY} minutes.")
        queue.enqueue_in(time_delta=timedelta(minutes=constants.UPDATE_DELAY), func=periodic_update)
        # FIXME: for some reason this makes the job execute 5-6 minutes later on heroku rather than 10. cause is unknown


def periodic_update():
    """Job that runs periodically and makes sure to run update() on all the players."""
    player_query = Player.objects.all().only("name")
    queue = get_queue()
    jobs = []
    for player in player_query:
        jobs.append(queue.prepare_data(update, [player.name]))
    if jobs:  # only execute if there are jobs to be done, prevents a value errors
        # TODO: Maybe put a try / except here.
        with queue.connection.pipeline() as pipe:
            enqueued_jobs = queue.enqueue_many(jobs, pipeline=pipe)
            pipe.execute()
        dependency = Dependency(jobs=enqueued_jobs)
        queue.enqueue(enqueue_periodic, depends_on=dependency)
    else:
        queue.enqueue(enqueue_periodic)


def create_ladder_job(
    name: str,
    start_date: datetime,
    end_date: datetime,
    player_platform: str,
    is_absolute: bool,
    ignore_unranked: bool,
) -> int:
    """Job that creates a ladder in the background. Assumes all data have been checked beforehand.

    Args:
        name (str): The name of the ladder.
        start_date (DateTime): When it will start.
        end_date (DateTime): When it will end
        player_platform (str): An array of (player, platform) tuples.
        is_absolute (bool): If true, the ranking will be absolute (whoever with higher rank wins). If not, it will be relative (whoever climbs the most from its starting rank wins)
        ignore_unranked (bool): Wether to show or not show unranked players.

    Returns:
        int: The ID of the recently created ladder. Used to redirect users in the frontend.
    """
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
        print(f"Searching player {item[0]} {item[1]}")
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

    asyncio.run(async_wrapper(asyncio.gather, *tasks))

    return ladder.id
