# Deployment

This document covers running Porvoz in containers, locally and on a single
remote host (e.g. an AWS EC2 student instance).

## Prerequisites

- Docker 24+
- Docker Compose v2 (`docker compose`, not `docker-compose`)
- A domain or public IP that can receive Twilio webhooks (HTTPS recommended)

## Required environment variables

Create `.env` at the repo root. None of these have safe defaults in production —
the app will refuse to start if any is missing.

```env
# --- Django ---
DJANGO_SECRET_KEY=<random 50+ chars>
ALLOWED_HOSTS=porvoz.example.com,www.porvoz.example.com

# --- Database & cache ---
DB_PASSWORD=<strong password>          # used by docker-compose to seed Postgres
DATABASE_URL=postgresql://porvoz:<DB_PASSWORD>@db:5432/porvoz
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# --- Email (Gmail SMTP) ---
EMAIL_HOST_USER=porvozcolombia@gmail.com
EMAIL_HOST_PASSWORD=<app password>
DEFAULT_FROM_EMAIL=Porvoz <porvozcolombia@gmail.com>

# --- Twilio ---
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=+1xxxxxxxxxx
TWILIO_BASE_URL=https://porvoz.example.com

# --- Gemini ---
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

`.env` is excluded from both git and the Docker build context.

## Production stack

```bash
docker compose up -d --build
```

Services started:

| Service        | Image / build                | Port (host)        |
| -------------- | ---------------------------- | ------------------ |
| `db`           | `postgres:16-alpine`         | (internal)         |
| `redis`        | `redis:7-alpine`             | (internal)         |
| `web`          | `docker/django/Dockerfile`   | (internal :8000)   |
| `celery-worker`| same image                   | —                  |
| `celery-beat`  | same image                   | —                  |
| `nginx`        | `nginx:alpine`               | 80 / 443           |

The `web`, `celery-worker`, and `celery-beat` services share one image. Compose
respects healthchecks, so:

- `web` waits for `db` and `redis` to be healthy.
- `nginx` waits for `web` to be healthy.

## Optional: Flower (task monitor)

```bash
docker compose --profile monitoring up -d flower
```

Exposes Flower on port `5555`. Do **not** expose this publicly without auth.

## Development stack

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Differences from production:

- `DJANGO_SETTINGS_MODULE=config.settings.development`
- `porvoz/` is bind-mounted into `/app` for hot reload
- `runserver` instead of gunicorn
- Web exposed directly on host port 8000 (no nginx)

For Twilio webhooks you still need a public URL — run `python scripts/ngrok_run.py`
in a side terminal and copy the printed URL into `.env` as `TWILIO_BASE_URL`.

## Single-host AWS deployment (sketch)

1. Provision an EC2 instance (Amazon Linux or Ubuntu, t3.small minimum).
2. Install Docker + Docker Compose plugin.
3. Allocate an Elastic IP and point a DNS A record at it.
4. Open ports 80/443 in the security group.
5. `git clone` this repo, place `.env` next to `docker-compose.yml`.
6. `docker compose up -d --build`.
7. Configure TLS — easiest is to drop a Let's Encrypt sidecar or terminate
   TLS at an ALB / CloudFront in front of the instance.
8. In the Twilio console, point the voice webhook at
   `https://<your-domain>/llamadas/webhook/voice/`.

## Operational checks

```bash
# Health
curl https://<your-domain>/api/health/

# Logs
docker compose logs -f web celery-worker celery-beat

# Apply a new migration without downtime (small migrations only)
docker compose exec web python manage.py migrate

# Open a Django shell
docker compose exec web python manage.py shell

# Inspect Celery tasks
docker compose --profile monitoring up -d flower
```

## Backups

`postgres_data` and `media_files` are named Docker volumes. Snapshot them with:

```bash
docker run --rm -v porvoz_postgres_data:/data -v "$PWD":/backup alpine \
    tar czf /backup/postgres-$(date +%F).tar.gz -C /data .
```

Schedule equivalent commands via cron / systemd-timer on the host.
