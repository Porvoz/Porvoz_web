"""
Top-level Django config package for the Porvoz project.
"""
from config.celery import app as celery_app

__all__ = ("celery_app",)
