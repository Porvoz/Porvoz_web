"""
Staging settings for Porvoz.

Extends production.py. Identical security posture to production but:
- Uses TWILIO_DRY_RUN=true by default (no real calls unless overridden)
- More verbose logging
- Relaxed ALLOWED_HOSTS (can include *.railway.app, ngrok, etc.)

Set DJANGO_SETTINGS_MODULE=config.settings.staging in .env for staging deploys.
"""

import os

import sentry_sdk

from .production import *  # noqa: F401, F403

# ------------------------------------------------------------------
# Override: safe defaults for staging
# ------------------------------------------------------------------

# Prevent accidental real Twilio calls unless explicitly enabled in env
if not os.getenv("TWILIO_DRY_RUN"):
    os.environ.setdefault("TWILIO_DRY_RUN", "true")

# Staging banner in logs
_ENV_LABEL = "staging"

# Relax ALLOWED_HOSTS for ephemeral staging domains
_extra_hosts = os.getenv("STAGING_ALLOWED_HOSTS", "")
if _extra_hosts:
    ALLOWED_HOSTS = ALLOWED_HOSTS + [h.strip() for h in _extra_hosts.split(",") if h.strip()]  # noqa: F405

# More verbose logging in staging — easier to trace issues
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405

# Sentry: tag events as staging
if sentry_sdk.Hub.current.client:
    sentry_sdk.set_tag("environment", _ENV_LABEL)
