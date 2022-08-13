web: gunicorn SoloQTracker.wsgi:application
worker: python manage.py rqworker high default --with-scheduler