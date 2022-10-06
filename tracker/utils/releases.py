from . import constants
import aiohttp
import sentry_sdk
import traceback
from django_rq import get_queue
from datetime import timedelta


async def check_releases():
    """Periodically check for updates. Will stop checking if an update is found at least once."""
    # FIXME: This hits ratelimit for some reason
    updates = False
    print("Checking if new releases exist...")
    url = f"https://api.github.com/repos/{constants.RELEASE_USER}/{constants.RELEASE_REPO}/releases/latest"
    try:
        current_release = constants.RELEASE_VERSION
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.json()
                new_release = content["tag_name"]
        if current_release != new_release:
            release_url = f"https://github.com/{constants.RELEASE_USER}/{constants.RELEASE_REPO}/releases/latest"
            message = f"""New version found. You are running {current_release} and {new_release} is available in GitHub.
            Go to {release_url} to download the newest version."""
            print(message)
            sentry_sdk.capture_message(message)
            updates = True
        else:
            print("No updates found!")
    except Exception as err:
        sentry_sdk.capture_exception(err)
        traceback.print_exc()

    queue = get_queue("low")
    jobs = [x.func for x in queue.jobs]
    # Stop checking for updates if we know they are available. Also never enqueue multiple times, which may cause issues when restarting the server such as in Heroku.
    if not updates and check_releases not in jobs:
        queue.enqueue_in(
            time_delta=timedelta(minutes=constants.RELEASE_CHECK_DELAY),
            func=check_releases,
        )
