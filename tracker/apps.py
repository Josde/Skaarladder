from django.apps import AppConfig


class TrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tracker"

    def ready(self):
        import os

        if os.environ.get("RUN_MAIN", None) != "true":
            # Prevents this from running twice when using development server. See: https://stackoverflow.com/a/52430581
            from django_rq import get_queue
            import tracker.updater.updater_jobs as updater_jobs

            queue = get_queue("default")
            low_queue = get_queue("low")
            if updater_jobs.periodic_update not in [x.func for x in queue.jobs] and not (os.getenv("DEBUG", False)):
                # pass
                queue.enqueue(updater_jobs.periodic_update)
                low_queue.enqueue(updater_jobs.check_releases)
