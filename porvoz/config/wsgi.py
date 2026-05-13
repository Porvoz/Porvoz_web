"""
WSGI config for Porvoz project.
"""

import os

from django.core.wsgi import get_wsgi_application

_env = os.environ.get("DJANGO_ENVIRONMENT", "development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{_env}")

application = get_wsgi_application()
