import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------
# SEGURIDAD
# ---------------------------------------------------

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-in-production")

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = ["*"]


# ---------------------------------------------------
# CSRF / NGROK / REPLIT
# ---------------------------------------------------

CSRF_TRUSTED_ORIGINS = []

if os.environ.get("TWILIO_BASE_URL"):
    CSRF_TRUSTED_ORIGINS.append(os.environ["TWILIO_BASE_URL"])

if os.environ.get("REPLIT_DOMAINS"):
    for domain in os.environ["REPLIT_DOMAINS"].split(","):
        CSRF_TRUSTED_ORIGINS.append(f"https://{domain.strip()}")


# ---------------------------------------------------
# APLICACIONES
# ---------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "contacts",
    "reminders",
    "calls",
    "core.apps.CoreConfig",
]


# ---------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ---------------------------------------------------
# URLS
# ---------------------------------------------------

ROOT_URLCONF = "porvoz.urls"

WSGI_APPLICATION = "porvoz.wsgi.application"


# ---------------------------------------------------
# TEMPLATES
# ---------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]


# ---------------------------------------------------
# BASE DE DATOS
# ---------------------------------------------------

_db_url = os.environ.get("DATABASE_URL")

if _db_url:
    DATABASES = {
        "default": dj_database_url.config(
            env="DATABASE_URL",
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ---------------------------------------------------
# INTERNACIONALIZACIÓN
# ---------------------------------------------------

LANGUAGE_CODE = "es-es"

# usa variable del .env si existe
TIME_ZONE = os.environ.get("APP_TIMEZONE", "America/Bogota")

USE_I18N = True
USE_TZ = True


# ---------------------------------------------------
# ARCHIVOS ESTÁTICOS
# ---------------------------------------------------

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = []

static_dir = BASE_DIR / "static"

if static_dir.exists():
    STATICFILES_DIRS.append(static_dir)


# ---------------------------------------------------
# MODELOS
# ---------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------
# LOGGING (para depurar Twilio / Gemini)
# ---------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}