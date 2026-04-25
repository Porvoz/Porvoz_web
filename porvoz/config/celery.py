"""
Celery app for Porvoz.

Para iniciar el worker:
    celery -A config worker --loglevel=info

Para iniciar el beat scheduler (tareas periódicas):
    celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("porvoz")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
