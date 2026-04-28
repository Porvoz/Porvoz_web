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

# Email backend:
#   - Si hay credenciales SMTP en .env (EMAIL_HOST_USER + EMAIL_HOST_PASSWORD),
#     se usa SMTP real para que los correos lleguen al cuidador en desarrollo.
#   - Si no hay credenciales, fallback a consola (los correos se imprimen en stdout).
#   - Override manual: EMAIL_BACKEND en .env tiene la última palabra.
_smtp_listo = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend"
    if _smtp_listo
    else "django.core.mail.backends.console.EmailBackend",
)

# Celery: Run tasks synchronously in dev (no broker needed).
# To use real Celery: set REDIS_URL in .env and run celery worker + beat separately.
CELERY_BROKER_URL = "memory://"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = False  # Don't crash webhooks if email task fails
