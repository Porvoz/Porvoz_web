# =========================================================================
# Porvoz — Django + Celery (multi-stage build)
# Build context expected: repository root.
#
# Build: docker build -f docker/django/Dockerfile -t porvoz:latest .
# =========================================================================

# -------- Stage 1: builder ------------------------------------------------
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build-only dependencies. libpq-dev is needed to compile psycopg2 wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY porvoz/requirements.txt ./requirements.txt

RUN pip wheel --wheel-dir=/wheels --no-cache-dir -r requirements.txt gunicorn


# -------- Stage 2: runtime ------------------------------------------------
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PATH="/home/appuser/.local/bin:${PATH}"

# Runtime-only deps. libpq5 (not -dev) is enough to run psycopg2.
# curl is used by the Docker HEALTHCHECK below.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libjpeg62-turbo \
        zlib1g \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 1000 appuser \
    && useradd  --system --uid 1000 --gid appuser --create-home --shell /bin/bash appuser

WORKDIR /app

# Install pre-built wheels from the builder stage.
COPY --from=builder /wheels /wheels
COPY porvoz/requirements.txt ./requirements.txt
RUN pip install --no-index --find-links=/wheels -r requirements.txt gunicorn \
    && rm -rf /wheels

# Application source.
COPY --chown=appuser:appuser porvoz/ /app/

# Entrypoint lives next to the Dockerfile.
COPY --chown=appuser:appuser docker/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health endpoint exposed at /api/health/ — see config/health.py
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl --fail --silent http://localhost:8000/api/health/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
