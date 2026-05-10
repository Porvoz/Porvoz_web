"""
Production settings for Porvoz.
Extends base.py with prod-specific overrides: DEBUG=False, PostgreSQL, Redis, SMTP.
All sensitive vars must be in .env (DATABASE_URL, REDIS_URL, email credentials).
"""

from .base import *  # noqa
import re

DEBUG = False

# -----------------------------------------------------------------------------
# Fail-fast: every variable required to safely run the system in production
# must be present at import time. Better to crash on boot than at runtime in
# the middle of a Twilio webhook.
# -----------------------------------------------------------------------------
_REQUIRED_ENV = (
    "DJANGO_SECRET_KEY",
    "ALLOWED_HOSTS",
    "DATABASE_URL",
    "REDIS_URL",
    "CELERY_BROKER_URL",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_FROM_NUMBER",
    "TWILIO_BASE_URL",
    "GEMINI_API_KEY",
)
_missing = [name for name in _REQUIRED_ENV if not os.getenv(name)]
if _missing:
    raise RuntimeError(
        "Production startup aborted — missing required environment variables: "
        + ", ".join(_missing)
    )

if SECRET_KEY == "dev-secret-key-change-me":
    raise RuntimeError("DJANGO_SECRET_KEY must not use the development default in production")

# Security
_allowed = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ["*"]:
    raise RuntimeError("ALLOWED_HOSTS must be an explicit list of hostnames in production")

# Trust X-Forwarded-Proto from nginx proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # nginx handles TLS termination
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

_csrf_origins = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://54.164.24.119,https://54.164.24.119"
)

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in _csrf_origins.split(",")
    if origin.strip()
]

if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        f"http://{host}" for host in ALLOWED_HOSTS
    ]

    CSRF_TRUSTED_ORIGINS += [
        f"https://{host}" for host in ALLOWED_HOSTS
    ]
# Database: PostgreSQL — DATABASE_URL is already required by the fail-fast block above.
database_url = os.getenv("DATABASE_URL", "")
_m = re.match(
    r"postgres(?:ql)?://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)",
    database_url
)
if not _m:
    raise RuntimeError(f"Invalid DATABASE_URL format: {database_url}")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": _m.group(1),
        "PASSWORD": _m.group(2),
        "HOST": _m.group(3),
        "PORT": _m.group(4) or "5432",
        "NAME": _m.group(5),
        "CONN_MAX_AGE": 600,
        "ATOMIC_REQUESTS": True,
    }
}

# Cache: Redis — REDIS_URL is already required by the fail-fast block above.
redis_url = os.getenv("REDIS_URL", "")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": redis_url,
        "OPTIONS": {
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "socket_keepalive": True,
        },
    }
}

# Celery: Async task queue — CELERY_BROKER_URL is already required by the fail-fast block.
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", redis_url)
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "default"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Bogota"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300  # 5 min max per task
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Periodic task: scan for due Llamadas every 60s and dispatch one task per call.
# DatabaseScheduler upserts these entries into django_celery_beat tables on boot,
# so changes propagate even if the beat container is already running.
CELERY_BEAT_SCHEDULE = {
    "ejecutar-llamadas-pendientes": {
        "task": "apps.llamadas.tasks.ejecutar_llamadas_pendientes_task",
        "schedule": 60.0,
    },
    "verificar-estados-plan": {
        "task": "apps.usuarios.tasks.verificar_estados_plan_task",
        "schedule": 86400.0,
    },
    "reactivar-medicamentos-pausados": {
        "task": "apps.medicamentos.tasks.reactivar_medicamentos_pausados_task",
        "schedule": 86400.0,
    },
    "resumen-semanal": {
        "task": "apps.usuarios.tasks_email.enviar_resumen_semanal_task",
        "schedule": 604800.0,  # cada 7 días
    },
}

# Email: SMTP — credentials are already required by the fail-fast block.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
