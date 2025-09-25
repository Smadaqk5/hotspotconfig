"""
Celery configuration for hotspot_config project.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')

app = Celery('hotspot_config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
