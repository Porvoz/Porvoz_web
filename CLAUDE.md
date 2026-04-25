# CLAUDE.md

This file provides guidance to Claude Code when working with the Porvoz project.

## Project Overview

**Porvoz** is a Django web application for managing medication reminders using automated voice calls. Caregivers register medications with dosing schedules and health conditions. The system sends automated reminders via voice calls, registers confirmations, and alerts when medications are not taken.

**Tech Stack:** Django 5.2, Django REST Framework, SQLite (dev) / PostgreSQL (prod), Tailwind CSS, Bootstrap Icons, Twilio (voice calls), Google Gemini (AI conversation), Celery + Redis (async tasks)

**Current Phase:** Sprint 3 completed. Celery/Redis integrated for async emails and call execution. PostgreSQL-ready via DATABASE_URL. `_conversaciones` migrated to Django cache. Email sending now async via tasks. **Architectural refactor completed:** proper file organization, Django admin registration, settings split (dev/prod), cross-cutting utilities moved to shared layer, email templates migrated to notificaciones app, full test coverage for all apps.

---

## Recent Architectural Improvements (Sprint 3.5)

### File Organization & Structure
- **`config/health.py`** — Moved health check from `llamadas/health.py` to `config/` (infrastructure concern, not domain-specific)
- **`apps/shared/decorators.py`** — Moved Twilio webhook decorators from `llamadas/` (cross-cutting utilities)
- **`apps/notificaciones/templates/notificaciones/emails/`** — Email templates moved from root `templates/emails/` (app-level asset ownership)
- **`scripts/ngrok_run.py`** — Development helper moved to dedicated `scripts/` folder

### Settings Split (base / development / production)
- **`config/settings/base.py`** — Shared settings only (apps, middleware, templates, auth, email defaults)
- **`config/settings/development.py`** — Dev overrides: DEBUG=True, SQLite, LocMemCache, console email, Celery disabled
- **`config/settings/production.py`** — Prod overrides: DEBUG=False, PostgreSQL required, Redis required, SMTP required, Celery enabled
- **Environment detection:** Use `DJANGO_SETTINGS_MODULE=config.settings.production` in production; defaults to development

### Django Admin Registration
All models now registered in Django admin for debugging and data inspection:
- `apps/core/admin.py` — Perfil
- `apps/pacientes/admin.py` — Paciente, Enfermedad
- `apps/medicamentos/admin.py` — Medicamento, HorarioMedicamento (with inline editing)
- `apps/notificaciones/admin.py` — Notificacion
- `apps/llamadas/admin.py` — Llamada, RespuestaLlamada, AuditoriaLog

### Test Coverage
New test files for previously untested apps:
- `apps/autenticacion/tests.py` — User registration, password reset validation
- `apps/usuarios/tests.py` — Profile changes, password validation, plan limits
- `apps/dashboard/tests.py` — Stats aggregation, call metrics, activity feed
- `apps/shared/tests.py` — TelefonoService, rate limiting, webhook deduplication

### Import Updates
- `config/urls.py` — health check import updated to `config.health`
- `apps/llamadas/views.py` — decorators import updated to `apps.shared.decorators`
- `apps/notificaciones/services/email_service.py` — template paths updated to `notificaciones/emails/`

---

## Development Setup

Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r porvoz/requirements.txt
```

Create `.env` file at repo root (`proyecto 2/.env`) — never commit this:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=+1xxxxxxxxxx
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_BASE_URL=https://your-ngrok-or-domain.com
DJANGO_SECRET_KEY=your-secret-key-here

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=porvozcolombia@gmail.com
EMAIL_HOST_PASSWORD=<gmail-app-password>
DEFAULT_FROM_EMAIL=Porvoz <porvozcolombia@gmail.com>

# Opcional — omitir en dev usa SQLite + LocMemCache sin Celery
DATABASE_URL=postgresql://user:pass@localhost:5432/porvoz
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

`manage.py` loads this `.env` automatically via `python-dotenv` from `Path(__file__).resolve().parent.parent / ".env"`.

---

## Common Commands

All commands from `porvoz/` directory:

| Task | Command |
|------|---------|
| **Run dev server** | `python manage.py runserver` |
| **Expose via ngrok** | `python ../scripts/ngrok_run.py` |
| **Execute calls in loop** | `python manage.py ejecutar_llamadas --loop --intervalo 60` |
| **Apply migrations** | `python manage.py migrate` |
| **Create superuser** | `python manage.py createsuperuser` |
| **Make migrations** | `python manage.py makemigrations` |
| **Run all tests** | `python manage.py test apps` |
| **Run app tests** | `python manage.py test apps.llamadas` |
| **Check issues** | `python manage.py check` |
| **Execute pending calls (once)** | `python manage.py ejecutar_llamadas` |

**Development workflow sin Redis (3 terminales):**
```bash
# Terminal 1: Django dev server
python manage.py runserver

# Terminal 2: ngrok para Twilio webhooks
python ../scripts/ngrok_run.py

# Terminal 3: Ejecutar llamadas (sin Celery)
python manage.py ejecutar_llamadas --loop --intervalo 60
```

**Development workflow con Redis/Celery (5 terminales):**
```bash
# Terminal 1: Django dev server
python manage.py runserver

# Terminal 2: ngrok para Twilio webhooks
python ../scripts/ngrok_run.py

# Terminal 3: Celery worker (procesa tareas: emails, llamadas)
celery -A config worker --loglevel=info

# Terminal 4: Celery beat (scheduler periódico de llamadas)
celery -A config beat --loglevel=info

# Terminal 5: Flower (monitoreo de tareas — opcional)
celery -A config flower
```

---

## Project Architecture

### Architecture Principles

- **SRP (Single Responsibility):** Each app has ONE clear responsibility
- **DIP (Dependency Inversion):** Services are HTTP-agnostic, views depend on services
- **No Fat Views:** Max 30 lines, only HTTP handling + redirect
- **No Fat Models:** Only fields + Meta class + `__str__()`
- **Service Layer:** All business logic in `@staticmethod` services
- **Dependency direction:** `core` ← `shared` ← domain apps ← presentation apps (never reverse)

### Why `core` and `shared` exist

- **`core/`** — `Perfil` is a foundation model referenced by every app. It cannot live in `usuarios` because that would force domain apps (`pacientes`, `medicamentos`) to import from a presentation app, creating circular dependencies. `core` has no business logic, only the model and context processor.
- **`shared/`** — `TelefonoService` is used by `autenticacion`, `usuarios`, and `pacientes`. Putting it in any of those would force the others to import cross-domain. `shared` is a pure utility layer with no domain knowledge.

### Directory Structure

```
porvoz/
├── templates/                         ← Global (base, sidebar, footer)
│   ├── base.html
│   ├── sidebar.html
│   ├── footer.html
│   └── guest_left_panel.html
│
├── config/
│   ├── settings/base.py               ← Email, auth, INSTALLED_APPS, SITE_ID=1
│   ├── urls.py                        ← Includes all apps
│   └── wsgi.py
│
└── apps/
    ├── core/                          ← Foundation layer: ONLY model + context processor
    │   ├── models.py                  (Perfil — 1:1 with User, has plan + expiration)
    │   ├── context_processors.py      (perfil_sidebar → adds perfil + no_leidas to every template)
    │   └── apps.py
    │
    ├── shared/                        ← Cross-cutting utilities (no domain logic)
    │   ├── services/
    │   │   └── telefono_service.py    (Parse, format, sanitize phones — used by 5 apps)
    │   ├── exceptions.py              (PorvozError base + NotificacionError)
    │   └── apps.py
    │
    ├── PRESENTATION APPS ─────────────────────────────
    │
    ├── autenticacion/
    │   ├── services/registro_service.py
    │   ├── forms.py                   (PorvozPasswordResetForm — validates email exists)
    │   ├── views.py / urls.py
    │   └── templates/autenticacion/
    │       ├── login.html
    │       ├── reset_password.html             ← Step 1: enter email
    │       ├── reset_password_done.html        ← Step 2: check your inbox
    │       ├── reset_password_confirm.html     ← Step 3: set new password
    │       └── reset_password_complete.html    ← Step 4: success
    │
    ├── usuarios/
    │   ├── services/
    │   │   ├── perfil_service.py      (Edit Perfil, change password, get_dias_restantes_plan, email preferences)
    │   │   └── planes_service.py      (PlanService — limits enforcement + PLAN_LIMITS + PLANES_DATA)
    │   ├── forms.py / views.py / urls.py
    │   └── templates/usuarios/
    │       ├── edit_profile.html      ← Email preferences section with 5 restrictive checkboxes
    │       └── change_password.html   ← 2-column layout, strength bar, requirements checklist
    │
    ├── dashboard/
    │   ├── services/dashboard_service.py   (patients, call stats, reminders, activity)
    │   ├── views.py / urls.py
    │   └── templates/dashboard/
    │       └── dashboard.html         ← Amber alert for patients without meds, call stats card
    │
    ├── legal/
    │   ├── views.py / urls.py
    │   └── templates/legal/
    │
    ├── DOMAIN APPS ─────────────────────────────────
    │
    ├── pacientes/
    │   ├── models.py                  (Paciente, Enfermedad)
    │   ├── services/paciente_service.py
    │   ├── forms.py / views.py / urls.py
    │   ├── templates/pacientes/
    │   │   ├── detalle_paciente.html  ← Call badge, report download modal (Adherencia/Incumplimientos/Auditoría)
    │   │   ├── listar_pacientes.html  ← Patient cards, "Ver detalles" button (w-full, prominent, shadow-lg)
    │   │   └── historial_llamadas_paciente.html  ← Filter by medication dropdown
    │   └── tests/test_services.py
    │
    ├── medicamentos/
    │   ├── models.py                  (Medicamento — instrucciones_llamada is CharField max=200)
    │   ├── services/medicamento_service.py
    │   ├── forms.py / views.py / urls.py
    │   ├── templates/medicamentos/    ← Character counter (0/200) on instrucciones_llamada
    │   └── tests/test_services.py
    │
    ├── notificaciones/
    │   ├── models.py                  (Notificacion — added PRIORIDAD field + url_detalle)
    │   ├── services/
    │   │   ├── notificacion_service.py (CRUD, filtering, priorities, email preferences)
    │   │   └── email_service.py       (HTML email templates, preference checking, context links)
    │   ├── forms.py / views.py / urls.py
    │   ├── templates/notificaciones/
    │   │   ├── notifications.html     ← Compacted filters, priority badges (critica/urgente/normal/baja)
    │   │   └── emails/                ← HTML email templates with branding
    │   │       ├── base_email.html
    │   │       ├── notificacion_alerta.html
    │   │       ├── notificacion_toma_confirmada.html
    │   │       ├── notificacion_toma_no_confirmada.html
    │   │       ├── notificacion_llamada_no_atendida.html
    │   │       └── notificacion_toma_aplazada.html
    │   └── tests/test_services.py
    │
    └── llamadas/                      ← Sprint 2 ✓ + reports ✓
        ├── models.py                  (Llamada, RespuestaLlamada)
        ├── services/
        │   ├── llamada_service.py     (Crear, ejecutar, sanitizar, registrar, alertas)
        │   ├── proveedor_voz_service.py  (Twilio + Gemini, max 2 oraciones, 280 chars)
        │   └── reporte_service.py     (CSV reports: Adherencia, Incumplimientos, Auditoría)
        ├── forms.py                   (FiltroHistorialLlamadasForm)
        ├── views.py                   (MAX_TURNOS=4, MAX_HISTORIAL_LINEAS=8)
        ├── urls.py
        ├── templates/llamadas/
        │   └── historial.html         ← Filter by medication
        ├── management/commands/ejecutar_llamadas.py
        ├── tests/test_services.py
        └── apps.py
```

---

## Core Concepts

### User Model
- Only 1 type of user: "Cuidador" (self-caregiver or caregiver for others)
- Extended via `Perfil` (1:1 with User) in `apps.core`
- Has plans with expiration date

### Plans

| Key | Display | Price | Patients | Meds/patient | Calls/month |
|-----|---------|-------|----------|--------------|-------------|
| `freemium` | Básico | $0 | 1 | 3 | 5 |
| `growth` | Familiar | $29.900 COP | 5 | 10 | 60 |
| `multi_business` | Profesional | $89.900 COP | 15 | unlimited | 250 |

Plan logic lives in `apps.usuarios.services.planes_service.PlanService`. Plan is enforced at:
- Patient creation (`agregar_paciente_view`)
- Medication creation (`agregar_medicamento_view`)
- Call execution (`ejecutar_llamadas_pendientes`)

To change a user's plan during dev: edit `Perfil.plan` directly in Django admin or shell.

### Data Relationships
```
User (Django)
  └─ Perfil (1:1)  ← in apps.core
     ├─ Pacientes (1:N)
     │  ├─ Medicamentos (1:N)
     │  │  ├─ HorarioMedicamento (1:N)
     │  │  ├─ instrucciones_llamada (CharField max=200) ← IA context for call
     │  │  ├─ minutos_antes_llamada  ← call scheduling offset
     │  │  └─ Llamadas (1:N)
     │  │     └─ RespuestaLlamada (1:1)
     │  ├─ Enfermedades (1:N)
     │  └─ Notificaciones (1:N)
     └─ Notificaciones (1:N - alerts, reminders, system)
```

### Notification Types
- `TIPO_SISTEMA` — System events (patient added, medication created)
- `TIPO_RECORDATORIO` — Internal reminders (display only)
- `TIPO_ALERTA` — Alerts (call not answered, error, plan limit reached)

### Notification Priorities (Sprint 2.5)
- `PRIORIDAD_BAJA` — Confirmations, routine info (green badge)
- `PRIORIDAD_NORMAL` — Standard alerts, medication changes (blue badge)
- `PRIORIDAD_URGENTE` — Missed calls, non-adherence (orange badge)
- `PRIORIDAD_CRITICA` — Plan limits, system errors (red badge)

**Email Preferences** (Perfil model):
- `email_toma_confirmada` — Default False (not critical)
- `email_toma_no_confirmada` — Default False (non-critical)
- `email_llamada_no_atendida` — Default False (non-critical)
- `email_toma_aplazada` — Default False (non-critical)
- `email_urgente_minimo` — Default True (ONLY if True, send CRITICAL/URGENTE regardless of above preferences)

### Call States
```
Llamada.estado:
  programada → en_curso → completada
                        ↘ fallida

RespuestaLlamada.como_respondio:
  atendida | no_atendida | buzon
  (no_atendida / buzon → creates TIPO_ALERTA automatically)
```

### Call Safety Limits
- Max 4 conversation turns per call (`MAX_TURNOS = 4`)
- History sent to Gemini truncated to last 8 lines (`MAX_HISTORIAL_LINEAS = 8`)
- Gemini response truncated to 280 characters
- `instrucciones_llamada` capped at 200 chars (CharField) + sanitized for prompt injection
- System prompt: max 2 sentences, no personal data requests, no medical advice

### Service Organization

| Service | Location | Responsibility |
|---------|----------|-----------------|
| `RegistroService` | `apps.autenticacion.services` | Create User + Perfil |
| `PerfilService` | `apps.usuarios.services` | Edit Perfil, change password, dias_restantes_plan, email prefs |
| `PlanService` | `apps.usuarios.services.planes_service` | Enforce plan limits, usage stats |
| `DashboardService` | `apps.dashboard.services` | Patients, call stats (7d), reminders, activity |
| `PacienteService` | `apps.pacientes.services` | Patient CRUD, phone verification |
| `MedicamentoService` | `apps.medicamentos.services` | Medication CRUD, toggle |
| `NotificacionService` | `apps.notificaciones.services` | CRUD, filtering, priorities, email gateway |
| `EmailService` | `apps.notificaciones.services.email_service` | HTML email templates, preference checking |
| `LlamadaService` | `apps.llamadas.services` | Schedule, execute, sanitize, register responses |
| `ProveedorVozService` | `apps.llamadas.services` | Twilio calls + Gemini AI |
| `ReporteService` | `apps.llamadas.services.reporte_service` | CSV reports (Adherencia, Incumplimientos, Auditoría) |
| `TelefonoService` | `apps.shared.services` | Parse, format, sanitize phones |

---

## Development Patterns

### Adding a New Domain Feature

1. Create folder: `apps/<domain>/`
2. Add standard files: `models.py`, `services/<domain>_service.py`, `forms.py`, `views.py`, `urls.py`, `templates/<app>/`, `tests/test_services.py`
3. Register in `INSTALLED_APPS`
4. Run: `python manage.py makemigrations <app> && python manage.py migrate`
5. Update `config/urls.py`

### Adding a New Service Method

1. Write method in the appropriate service (`@staticmethod`)
2. Write tests in `apps/<app>/tests/test_services.py`
3. Return tuple `(success: bool, error_msg: Optional[str])` or data
4. Only raise `NotificacionError` from `apps.shared.exceptions`; other domain errors can be plain `ValueError`

### View Template

```python
@login_required
def my_view(request):
    """Max 30 lines. Only HTTP + redirect."""
    if request.method == "POST":
        form = MyForm(request.POST)
        if form.is_valid():
            try:
                result = MyService.do_something(**form.cleaned_data)
                messages.success(request, "Done!")
                return redirect("success_url")
            except SomeError as e:
                messages.error(request, str(e))
    else:
        form = MyForm()
    return render(request, "template.html", {"form": form})
```

### Webhook Pattern (Twilio)

```python
@csrf_exempt
@require_http_methods(["POST"])
def webhook_x(request):
    call_sid = request.POST.get("CallSid", "")
    # call service → return HttpResponse with TwiML or status 200
```

---

## Password Recovery

Uses Django's built-in 4-step `PasswordResetView` flow. Configured in `apps.autenticacion.urls`:

```
/autenticacion/restablecer/          → PasswordResetView (custom PorvozPasswordResetForm)
/autenticacion/restablecer/enviado/  → PasswordResetDoneView
/autenticacion/restablecer/<uid>/<token>/  → PasswordResetConfirmView
/autenticacion/restablecer/listo/    → PasswordResetCompleteView
```

`PorvozPasswordResetForm` adds a `clean_email()` that raises `ValidationError` if the email has no associated user (instead of silently sending nothing).

Email is sent via Gmail SMTP. Reset link uses `django.contrib.sites` (SITE_ID=1). To update the domain shown in the link:
```python
from django.contrib.sites.models import Site
Site.objects.filter(id=1).update(domain="localhost:8000", name="Porvoz")
```

---

## Dashboard

`DashboardService.obtener_datos_completos()` returns:
- `pacientes` — list with prefetched active medications and conditions
- `total_medicamentos` — count of active medications across all patients
- `proximos_recordatorios` — next scheduled medication times today
- `actividad_reciente` — last 5 notifications as activity feed
- `llamadas_semana` / `llamadas_atendidas_semana` / `llamadas_no_atendidas_semana` / `adherencia_semana` — call stats for last 7 days
- `pacientes_sin_medicamentos` — patients with 0 active medications (shown as amber warning banner + badge in table)

---

## Testing

```bash
python manage.py test apps                  # All tests
python manage.py test apps.llamadas
python manage.py test apps.pacientes
python manage.py test apps.medicamentos
python manage.py test apps.notificaciones
python manage.py test apps.core
```

**Tests should:**
- Only test services (HTTP-agnostic)
- Use `TestCase` from Django
- Cover happy path + error cases
- Be in `apps/<app>/tests/test_services.py`

---

## Code Style

- **Python:** PEP 8, Django conventions
- **Imports:** stdlib → third-party → Django → local
- **Views:** `@login_required`, no logic, call services
- **Forms:** Validate in `clean_<field>()` and `clean()` methods
- **Models:** Spanish field labels, Meta class with `db_table`
- **Services:** `@staticmethod`, HTTP-agnostic, return tuples or data
- **Naming:** `_` prefix for private functions, `get_` for getters, `create_/update_/delete_` for mutations

---

## Templates

- **Global templates:** `templates/` (base.html, sidebar.html, footer.html)
- **App templates:** `apps/<app>/templates/<app>/`
- **Styling:** Tailwind CSS utility classes (responsive by default)
- **Icons:** Bootstrap Icons
- **Design tokens:** `bg-slate-100`, `rounded-2xl`, `shadow-sm`, `font-black`, `border border-slate-200`

### Style Rules (MANDATORY)

- **No gradients** — never use `bg-gradient-*`, `from-*`, `to-*`, or CSS gradients
- **No folksy/vivid colors** — no purple/pink/cyan/lime/orange as primary backgrounds; no rainbow palettes
- **Allowed palette:** slate (primary UI), emerald (success/active), red (danger/error), amber (warning), white (cards)
- **Serious and elegant** — the app handles medical reminders; tone should be clean, trustworthy, professional
- **Buttons:** `bg-slate-700 text-white` (primary), `bg-white border border-slate-300 text-slate-700` (secondary), `bg-red-600 text-white` (danger)
- **Cards:** always `bg-white rounded-2xl border border-slate-200 shadow-sm`
- **Badges/pills:** use `bg-emerald-100 text-emerald-700` (success), `bg-red-100 text-red-700` (error), `bg-amber-100 text-amber-800` (warning), `bg-slate-100 text-slate-700` (neutral)

---

## Voice Calls — Sprint 2 Implementation

### Flow

```
Medicamento (instrucciones_llamada + minutos_antes_llamada)
  ↓
LlamadaService.programar_llamadas_medicamento()
  ↓
python manage.py ejecutar_llamadas [--loop --intervalo 60]
  ↓
LlamadaService.ejecutar_llamadas_pendientes()
  → PlanService.puede_realizar_llamada() check
  → LlamadaService._sanitizar_mensaje()
  ↓
ProveedorVozService.disparar_llamada(numero, mensaje, voice_url, status_url)
  ↓
Twilio → POST /llamadas/webhook/voice/?llamada_id=X&mensaje=...
  ↓
ProveedorVozService.generar_respuesta_ia()  ← Gemini (max 2 sentences, 280 chars)
  ↓
Twilio → POST /llamadas/webhook/gather/  (up to MAX_TURNOS=4 turns)
  ↓
Twilio → POST /llamadas/webhook/status/
  ↓
LlamadaService.registrar_estado_final()
  ↓
Si no_atendida/buzon → NotificacionService.crear_notificacion_alerta()
```

### Environment Variables Required

| Variable | Description |
|---|---|
| `TWILIO_ACCOUNT_SID` | Account SID from twilio.com/console |
| `TWILIO_AUTH_TOKEN` | Auth token from twilio.com/console |
| `TWILIO_FROM_NUMBER` | Twilio number in E.164 format |
| `GEMINI_API_KEY` | API key from aistudio.google.com |
| `TWILIO_BASE_URL` | Public URL where Twilio sends webhooks (ngrok in dev) |

### Running Calls in Development

```bash
# 1. Expose local server publicly
ngrok http 8000

# 2. Set TWILIO_BASE_URL=https://<ngrok-id>.ngrok.io in .env

# 3. Run Django
python manage.py runserver

# 4. Run call scheduler (separate terminal)
python manage.py ejecutar_llamadas --loop --intervalo 60
```

---

## Security

- Always validate user ownership: `get_object_or_404(Model, id=..., usuario=request.user)`
- Soft deletes: Use `activo=False` instead of hard delete
- Phone numbers: Sanitize with `TelefonoService`
- Webhooks: `@csrf_exempt` only on Twilio webhook views
- Call messages: Sanitized via `LlamadaService._sanitizar_mensaje()` (truncate + strip prompt injection keywords)
- Environment: Never commit `.env` — it's in `.gitignore`

---

## Performance

- Use `.select_related()` for ForeignKey
- Use `.prefetch_related()` for reverse relations / OneToOne
- Add indexes on `usuario`, `activo`, `fecha_programada`
- Voice conversation state (`_conversaciones` dict) is in-memory — fine for MVP, use Redis/cache in production

---

## Claude Code Guidance

**Git Commits:**
- Do NOT commit changes unless explicitly requested ("haz el commit", "crea un commit", etc.)
- Always verify `.env` is in `.gitignore` before any commit
- Never commit `.claude/` settings or temporary files

**Communication Style:**
- Be concise — no summaries at end of responses unless requested
- Avoid unnecessary recaps or "I've completed X" statements
- Answer directly without preamble
- In outputs/context, prioritize brevity (this saves token budget for future conversations)

---

## Docker / Production Stack

The repository ships with a production-ready container stack and a development overlay.

### Layout

```
proyecto-2/
├── docker/
│   ├── django/Dockerfile        # multi-stage build, non-root appuser
│   ├── django/entrypoint.sh
│   └── nginx/default.conf       # reverse proxy + static/media serving
├── docker-compose.yml           # production: db + redis + web + workers + nginx
├── docker-compose.dev.yml       # overlay: bind-mount source, runserver, no nginx
├── scripts/ngrok_run.py
└── docs/architecture.md, deployment.md
```

The Docker build context is the repository **root** (not `porvoz/`), so the
Dockerfile copies both `porvoz/` and `docker/django/entrypoint.sh`.

### Running the stack

```bash
# Production
docker compose up -d --build

# Production + Flower (task monitor)
docker compose --profile monitoring up -d

# Development (hot reload, dev settings, port 8000 on host)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Production env vars (fail-fast)

`config/settings/production.py` aborts at import time if any of these is missing:
`DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, `REDIS_URL`,
`CELERY_BROKER_URL`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`,
`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`,
`TWILIO_BASE_URL`, `GEMINI_API_KEY`. `ALLOWED_HOSTS=*` is also rejected.

### Celery beat schedule

Production registers one periodic task in `CELERY_BEAT_SCHEDULE`:
`apps.llamadas.tasks.ejecutar_llamadas_pendientes_task` every 60 s. The
`DatabaseScheduler` upserts this entry into `django_celery_beat` tables on boot.

### pyproject.toml

`porvoz/pyproject.toml` declares project metadata plus optional `dev` and `test`
dependency groups, and configures **ruff** (replacing flake8) and pytest.
`requirements.txt` is still the install source for Docker builds — pyproject is
metadata-only for now.

See `docs/architecture.md` and `docs/deployment.md` for the long form.

---

## Sprint 3+ Ideas

- **Celery + Redis:** Replace management command loop with proper async task queue
- **Call retry:** If `no_atendida`, retry after N minutes (configurable per medicamento)
- **Multi-schedule UI:** Form to add/edit multiple `HorarioMedicamento` per day
- **Date range filter:** In historial_llamadas view
- **Twilio signature validation:** Verify webhook authenticity (`X-Twilio-Signature`)
- **Conversation persistence:** Store `_conversaciones` in Django cache / Redis
- **Payment integration:** Stripe/Wompi for plan upgrades (plan changes currently done manually via admin/shell)

---

## Removed/Deprecated

- ❌ `apps.recordatorios` — Merged into `Notificacion.TIPO_RECORDATORIO` + automatic calls
- ❌ `apps.cuidadores` — No RBAC; "cuidador" is just User with Perfil
- ❌ External apps (`calls/`, `contacts/`, `reminders/`, `ai/`) — Prototype, not used
- ❌ `apps.shared.services.planes_service` — Was a shim re-exporting from `usuarios.services.planes_service`; deleted. Import directly from `apps.usuarios.services.planes_service`
- ❌ `PacienteError`, `MedicamentoError`, `PerfilError`, `AuthError`, `PlanError` — Were defined in `shared.exceptions` but never instantiated anywhere; removed. Only `PorvozError` (base) and `NotificacionError` remain
