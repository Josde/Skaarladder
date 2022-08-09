from django.apps import AppConfig


class TrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tracker"

    def ready(self):
        import os

        if os.environ.get("RUN_MAIN", None) != "true":
            # Prevents this from running twice when using development server. See: https://stackoverflow.com/a/52430581
            import tracker.updater.updater_jobs as updater_jobs
            from tracker.utils import constants
            from django_rq import get_queue
            from datetime import datetime

            # eventually change this to be a singleton connection for efficiency
            queue = get_queue("default")
            if updater_jobs.periodic_update not in [x.func for x in queue.jobs]:
                queue.enqueue(updater_jobs.periodic_update)
