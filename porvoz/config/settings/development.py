"""
Development settings for Porvoz.
Extends base.py with dev-specific overrides: DEBUG=True, SQLite, LocMemCache, console email.
"""

from .base import *  # noqa

DEBUG = True

# Database: SQLite for local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Cache: FileBasedCache para dev — persiste entre reinicios del servidor,
# evita perder conversaciones activas de Twilio cuando se reinicia Django.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / ".cache",
        "TIMEOUT": 600,  # 10 min — TTL de conversaciones activas
    }
}

# Email: Console backend (prints to stdout instead of sending)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery: Run tasks synchronously in dev (no broker needed).
# To use real Celery: set REDIS_URL in .env and run celery worker + beat separately.
CELERY_BROKER_URL = "memory://"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = False  # Don't crash webhooks if email task fails
