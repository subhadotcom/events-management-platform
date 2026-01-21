web: gunicorn events_platform.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A events_platform worker -l info
beat: celery -A events_platform beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
