import os
import sys
from django.apps import AppConfig


class RemindersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reminders"

    def ready(self):
        cmds_sin_scheduler = ("migrate", "makemigrations", "collectstatic", "shell", "check", "dbshell")
        if len(sys.argv) > 1 and sys.argv[1] in cmds_sin_scheduler:
            return

        es_runserver = len(sys.argv) > 1 and sys.argv[1] == "runserver"
        if es_runserver:
            if os.environ.get("RUN_MAIN") != "true":
                return
        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"No se pudo iniciar el programador de tareas: {e}")
