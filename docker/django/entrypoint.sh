#!/bin/bash
set -e

echo "[Entrypoint] Starting Django app..."

cd /app

export DJANGO_SETTINGS_MODULE=config.settings.production

echo "[Entrypoint] Ejecutando migraciones..."
python manage.py migrate --noinput

echo "[Entrypoint] Ejecutando collectstatic..."
python manage.py collectstatic --noinput

# =========================
# CELERY WORKER
# =========================
if [ "$1" = "celery-worker" ]; then
    echo "[Entrypoint] Iniciando Celery Worker..."
    exec celery -A config worker -l info
fi

# =========================
# CELERY BEAT
# =========================
if [ "$1" = "celery-beat" ]; then
    echo "[Entrypoint] Iniciando Celery Beat..."
    exec celery -A config beat -l info
fi

# =========================
# FLOWER
# =========================
if [ "$1" = "flower" ]; then
    echo "[Entrypoint] Iniciando Flower..."
    exec celery -A config flower --port=5555
fi

# =========================
# DJANGO WEB
# =========================
echo "[Entrypoint] Iniciando Gunicorn..."

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:10000 \
    --workers 4 \
    --timeout 120
