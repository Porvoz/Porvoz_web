# Architecture

## Overview

Porvoz is a Django 5 medication-reminder platform. Caregivers register patients
and medications; the system places automated voice calls (Twilio) to confirm
that each dose was taken, and uses Gemini to handle ambiguous spoken responses.

Architecture follows a strict service-layer pattern: views handle only HTTP,
services hold all business logic, models hold only data.

```
HTTP / Twilio webhook ──► Django view (≤30 lines)
                                 │
                                 ▼
                         Service layer (@staticmethod)
                                 │
                          ┌──────┴───────┐
                          ▼              ▼
                       Models     External providers
                                  (Twilio / Gemini /
                                   SMTP / Redis)
```

## Apps

| App              | Layer        | Responsibility                                        |
| ---------------- | ------------ | ----------------------------------------------------- |
| `core`           | foundation   | `Perfil` model + global context processor             |
| `shared`         | utilities    | Phone parsing, webhook decorators, common exceptions  |
| `autenticacion`  | presentation | Sign up, login, password reset                        |
| `usuarios`       | presentation | Profile editing, plan limits, email preferences       |
| `dashboard`      | presentation | Aggregated stats and activity feed                    |
| `legal`          | presentation | Static pages (terms, privacy)                         |
| `pacientes`      | domain       | Patients and conditions                               |
| `medicamentos`   | domain       | Medications, schedules, instructions for the AI       |
| `notificaciones` | domain       | Notifications + transactional email                   |
| `llamadas`       | domain       | Voice calls, Twilio integration, Gemini conversation  |

Dependency direction is one-way: `core ← shared ← domain ← presentation`.

## Voice-call flow

```
Beat scheduler (Celery)
        │
        ▼
ejecutar_llamadas_pendientes_task ── enqueues one task per due call
        │
        ▼
ejecutar_llamada_task
        │
        ▼
LlamadaService → ProveedorVozService.disparar_llamada
        │
        ▼
Twilio places the call ──► /llamadas/webhook/voice/
                                   │ (deduplicated by CallSid)
                                   ▼
                          Static TwiML or Gemini response
                                   │
                                   ▼
                      /llamadas/webhook/gather/  (up to 4 turns)
                                   │
                                   ▼
                      /llamadas/webhook/status/  (final state, alerts)
```

Safety filters short-circuit Gemini for two cases:

- **Emergencia médica** — keyword detection on the patient's transcript triggers
  `MSG_EMERGENCIA` and a critical email that bypasses user preferences.
- **Rechazo de tratamiento** — same pattern, with `MSG_RECHAZO`.

## Settings split

```
config/settings/
├── base.py          # shared: apps, middleware, templates, auth
├── development.py   # SQLite, LocMemCache, console email, no Celery required
└── production.py    # PostgreSQL, Redis, SMTP, Celery beat, fail-fast env check
```

`production.py` aborts at import time if any required env var is missing.

## Background jobs

- **Celery worker** processes ad-hoc tasks (emails, individual call dispatch).
- **Celery beat** uses `django_celery_beat.schedulers:DatabaseScheduler`. The
  `ejecutar-llamadas-pendientes` schedule is registered via
  `CELERY_BEAT_SCHEDULE` and runs every 60 s.
- **Flower** (optional) monitors workers; start with the `monitoring` profile.

## External services

| Provider | Purpose                       | Env var                                      |
| -------- | ----------------------------- | -------------------------------------------- |
| Twilio   | Outbound voice calls          | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `TWILIO_BASE_URL` |
| Gemini   | AI for ambiguous responses    | `GEMINI_API_KEY`                             |
| Gmail    | Transactional email           | `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`     |
| Postgres | Primary data store            | `DATABASE_URL`                               |
| Redis    | Cache, Celery broker          | `REDIS_URL`, `CELERY_BROKER_URL`             |

## Repository layout

```
proyecto-2/
├── docker/
│   ├── django/Dockerfile + entrypoint.sh   # multi-stage, non-root
│   └── nginx/default.conf
├── docker-compose.yml                      # production stack
├── docker-compose.dev.yml                  # development overlay
├── porvoz/                                 # Django project
│   ├── apps/
│   ├── config/settings/{base,development,production}.py
│   ├── pyproject.toml
│   └── requirements.txt
├── scripts/
│   └── ngrok_run.py
└── docs/
    ├── architecture.md
    └── deployment.md
```
