"""
Settings package for Porvoz.

Structure:
- base.py: Shared settings across all environments
- development.py: Dev overrides (DEBUG=True, SQLite, LocMemCache, console email)
- production.py: Production overrides (DEBUG=False, PostgreSQL, Redis, SMTP)

By default, imports development settings. Set DJANGO_SETTINGS_MODULE to use production:
  export DJANGO_SETTINGS_MODULE=config.settings.production
"""

from .development import *  # noqa
