#!/bin/bash
# Porvoz — Backup automático de base de datos PostgreSQL
# Uso: bash scripts/backup_db.sh
# Cron diario a la 2am:
#   0 2 * * * /path/to/porvoz/scripts/backup_db.sh >> /var/log/porvoz_backup.log 2>&1
set -e

BACKUP_DIR="${BACKUP_DIR:-/backups/porvoz}"
DB_NAME="${POSTGRES_DB:-porvoz}"
DB_USER="${POSTGRES_USER:-porvoz}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
KEEP_DAYS="${KEEP_DAYS:-30}"

mkdir -p "$BACKUP_DIR"

FILENAME="porvoz_$(date +%Y%m%d_%H%M%S).sql.gz"
FILEPATH="$BACKUP_DIR/$FILENAME"

echo "[backup] $(date) — Starting backup → $FILEPATH"
PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    "$DB_NAME" | gzip > "$FILEPATH"

SIZE=$(du -sh "$FILEPATH" | cut -f1)
echo "[backup] $(date) — Done. Size: $SIZE"

# Eliminar backups más viejos que KEEP_DAYS días
DELETED=$(find "$BACKUP_DIR" -name "porvoz_*.sql.gz" -mtime +$KEEP_DAYS -delete -print | wc -l)
echo "[backup] Cleaned $DELETED old backup(s) (older than $KEEP_DAYS days)"
