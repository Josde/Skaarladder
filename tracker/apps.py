from django.apps import AppConfig
from SoloQTracker.settings import DEBUG
from .utils import constants


class TrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tracker"

    def ready(self):
        import os

        if os.environ.get("RUN_MAIN", None) != "true":
            # Prevents this from running twice when using development server. See: https://stackoverflow.com/a/52430581
            from django_rq import get_queue
            from decouple import config
            import tracker.updater.updater_jobs as updater_jobs
            import tracker.utils.releases as releases

            # Enqueue periodic tasks (release check and periodic user update)
            queue = get_queue("default")
            jobs = [
                x.func for x in queue.jobs
            ]  # Jobs that are currently enqueued, used to prevent queuing something that was already queued.
            if constants.RELEASE_CHECK and releases.check_releases not in jobs:
                queue.enqueue(releases.check_releases)
            if updater_jobs.periodic_update not in jobs and not DEBUG:
                queue.enqueue(updater_jobs.periodic_update)
