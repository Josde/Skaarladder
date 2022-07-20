from django.apps import AppConfig


class TrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'
    
    def ready(self):
        from tracker.updater.updater_thread import UpdaterThread
        import threading
        t = UpdaterThread()
        t.start()
        
