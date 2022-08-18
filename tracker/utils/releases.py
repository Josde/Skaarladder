from . import constants
import aiohttp
import sentry_sdk
import traceback
from asgiref.sync import sync_to_async
from django_rq import get_queue
from SoloQTracker.settings import BASE_DIR
from datetime import timedelta


async def check_releases():
    """Periodically check for updates. Will stop checking if an update is found at least once."""
    updates = False
    print("Checking if new releases exist...")
    URL = f"https://api.github.com/repos/{constants.RELEASE_USER}/{constants.RELEASE_REPO}/releases/latest"
    try:
        current_release = constants.RELEASE_VERSION
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                content = await response.json()
                new_release = content["tag_name"]
        if current_release != new_release:
            RELEASE_URL = f"https://github.com/{constants.RELEASE_USER}/{constants.RELEASE_REPO}/releases/latest"
            message = f"""New version found. You are running {current_release} and {new_release} is available in GitHub.
            Go to {RELEASE_URL} to download the newest version."""
            print(message)
            sentry_sdk.capture_message(message)
            updates = True
        else:
            print("No updates found!")
    except Exception as err:
        sentry_sdk.capture_exception(err)
        traceback.print_exc()

    if not updates:  # Stop checking for updates if we know they are availab.e.
        queue = get_queue("low")
        queue.enqueue_in(
            time_delta=timedelta(minutes=constants.RELEASE_CHECK_DELAY),
            func=check_releases,
        )
