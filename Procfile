web: gunicorn hotspot_config.wsgi --log-file -
worker: celery -A hotspot_config worker --loglevel=info
release: python manage.py migrate
