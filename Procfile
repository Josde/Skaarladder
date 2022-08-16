web: gunicorn SoloQTracker.wsgi:application
worker: python manage.py rqworker high default low --with-scheduler