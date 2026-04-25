#!/bin/sh
set -e

# Migraciones y assets estáticos solo se ejecutan en el contenedor web
# (gunicorn). Los workers de Celery comparten el volumen y solo necesitan
# arrancar — evitamos colisiones de migrate concurrente.
case "$1" in
  celery-worker)
    echo "[entrypoint] Starting Celery worker..."
    exec celery -A config worker --loglevel=info --concurrency=2
    ;;
  celery-beat)
    echo "[entrypoint] Starting Celery beat..."
    exec celery -A config beat --loglevel=info \
        --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ;;
  flower)
    echo "[entrypoint] Starting Flower..."
    exec celery -A config flower --address=0.0.0.0 --port=5555
    ;;
  *)
    echo "[entrypoint] Running migrations..."
    python manage.py migrate --noinput

    echo "[entrypoint] Collecting static files..."
    python manage.py collectstatic --noinput

    echo "[entrypoint] Starting Gunicorn..."
    exec gunicorn config.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers 2 \
      --timeout 120 \
      --access-logfile - \
      --error-logfile -
    ;;
esac
