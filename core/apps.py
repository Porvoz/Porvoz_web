import os
from django.apps import AppConfig


class CoreConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):

        # Evita que el scheduler se ejecute dos veces en runserver
        if os.environ.get("RUN_MAIN") != "true":
            return

        from reminders.scheduler import start_scheduler
        start_scheduler()