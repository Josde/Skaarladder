from django.apps import AppConfig


class TrackerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tracker"

    def ready(self):
        import os

        if (
            os.environ.get("RUN_MAIN", None) != "true"
        ):  # Prevents this from running twice when using development server. See: https://stackoverflow.com/a/52430581
            from tracker.updater.updater_thread import UpdaterThread
            from concurrent.futures import ThreadPoolExecutor, as_completed

            t = UpdaterThread(
                daemon=True
            )  # FIXME: Get a better fix than daemon=True for closing
            t.start()
