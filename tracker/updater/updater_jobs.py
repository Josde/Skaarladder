import threading
from tracker.models import Player, Challenge, Challenge_Player
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


def create_challenge_job(name, start_date, end_date, player_platform, is_absolute, ignore_unranked):
    # TODO: Validations here etc
    challenge = Challenge(
        name=name,
        start_date=start_date,
        end_date=end_date,
        is_absolute=is_absolute,
        ignore_unranked=ignore_unranked,
    )
    challenge.save()
    tasks = []
    players = []
    player_challenges = []
    for item in player_platform:
        print("Searching player {0} {1}".format(item[0], item[1]))
        try:
            player = Player.objects.get(name=item[0], platform=item[1])
        except Player.DoesNotExist:
            player = Player.create(name=item[0], platform=item[1])
            player.save()
            players.append(player)  # We only created non existing players to prevent violating PK uniqueness
            tasks.append(update(player))  # Only update if not in DB
        except Player.MultipleObjectsReturned:
            query = Player.objects.all().filter(name=item[0], platform=item[1])
            player = query[0]
        finally:
            player_challenge = Challenge_Player(
                player_id=player,
                challenge_id=challenge,
                starting_lp=0,
                starting_tier="UNRANKED",
                starting_rank="NONE",
            )
            player_challenges.append(player_challenge)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))
    for item in player_challenges:
        # TODO: Check how efficient this is in terms of queries and DB access time. Also, test this (battery is running out lol)
        # Bulk_update errors out for some reason here
        item.starting_lp = item.player_id.lp
        item.starting_tier = item.player_id.tier
        item.starting_rank = item.player_id.rank
        item.save()

    return challenge.id
