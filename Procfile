web: python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A backend worker --loglevel=info