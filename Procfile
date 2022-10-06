web: gunicorn -w 4 SoloQTracker.wsgi:application
worker: python manage.py rqworker high default low --with-scheduler