from django.apps import AppConfig
from .utils import constants


class TrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tracker"

    def ready(self):
        import os

        if os.environ.get("RUN_MAIN", None) != "true":
            # Prevents this from running twice when using development server. See: https://stackoverflow.com/a/52430581
            from django_rq import get_queue
            import tracker.updater.updater_jobs as updater_jobs
            import tracker.utils.releases as releases

            # Enqueue periodic tasks (release check and periodic user update)
            queue = get_queue("default")
            if constants.RELEASE_CHECK:
                queue.enqueue(releases.check_releases)
            if updater_jobs.periodic_update not in [x.func for x in queue.jobs] and not (os.getenv("DEBUG", False)):
                queue.enqueue(updater_jobs.periodic_update)
