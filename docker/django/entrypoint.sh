#!/bin/bash
set -e

echo "[Entrypoint] Starting Django app..."

cd /app/porvoz

# Detect environment: if DATABASE_URL is not set AND we're not in development, fail-fast
if [ -z "$DATABASE_URL" ]; then
  if [ "$DJANGO_ENVIRONMENT" = "production" ] || [ "$DJANGO_ENVIRONMENT" = "staging" ]; then
    echo "[Entrypoint] ERROR: DATABASE_URL must be set in production/staging environments"
    exit 1
  fi
  echo "[Entrypoint] DATABASE_URL not set; using docker-compose defaults..."
  export DATABASE_URL="postgresql://porvoz:porvoz_secret@db:5432/porvoz"
fi

# Set environment variables with fallbacks (only used if not already set)
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-dev-secret-key-docker-default}"
export DJANGO_ENVIRONMENT="${DJANGO_ENVIRONMENT:-development}"
export ALLOWED_HOSTS="${ALLOWED_HOSTS:-localhost,127.0.0.1,web}"
export REDIS_URL="${REDIS_URL:-redis://redis:6379/0}"
export CELERY_BROKER_URL="${CELERY_BROKER_URL:-redis://redis:6379/0}"
export CELERY_RESULT_BACKEND="${CELERY_RESULT_BACKEND:-redis://redis:6379/0}"
export EMAIL_HOST_USER="${EMAIL_HOST_USER:-noreply@porvoz.local}"
export EMAIL_HOST_PASSWORD="${EMAIL_HOST_PASSWORD:-dummy-password}"
export TWILIO_ACCOUNT_SID="${TWILIO_ACCOUNT_SID:-ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}"
export TWILIO_AUTH_TOKEN="${TWILIO_AUTH_TOKEN:-dummy-token}"
export TWILIO_FROM_NUMBER="${TWILIO_FROM_NUMBER:-+1234567890}"
export TWILIO_BASE_URL="${TWILIO_BASE_URL:-http://web:10000}"
export GEMINI_API_KEY="${GEMINI_API_KEY:-dummy-gemini-key}"

echo "[Entrypoint] Environment: $DJANGO_ENVIRONMENT"
echo "[Entrypoint] Database: $DATABASE_URL (host redacted)"

# Ejecutar collectstatic si no existe o si está vacío el volumen
if [ ! -d "/app/staticfiles" ] || [ -z "$(ls -A /app/staticfiles)" ]; then
    echo "[Entrypoint] Ejecutando collectstatic..."
    python manage.py collectstatic --noinput --clear --settings=config.settings.production --verbosity 2
    echo "[Entrypoint] ✓ Collectstatic completado"
fi

# Ejecutar migraciones
echo "[Entrypoint] Ejecutando migraciones..."
python manage.py migrate --settings=config.settings.production
echo "[Entrypoint] ✓ Migraciones completadas"

# Iniciar gunicorn
echo "[Entrypoint] Iniciando gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:10000 \
  --workers 4 \
  --worker-class sync \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
