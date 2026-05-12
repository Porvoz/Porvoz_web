#!/bin/bash
set -e

echo "[Entrypoint] Starting Django app..."

# Cambiar a directorio de la app
cd /app/porvoz

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
