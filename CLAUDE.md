# CLAUDE.md

This file provides guidance to Claude Code when working with the Porvoz project.

## Project Overview

**Porvoz** is a Django web application for managing medication reminders using automated voice calls. Caregivers register medications with dosing schedules and health conditions. The system sends automated reminders via voice calls, registers confirmations, and alerts when medications are not taken.

**Tech Stack:** Django 5.2, Django REST Framework, SQLite (dev), Tailwind CSS, Bootstrap Icons, Twilio (voice calls), Google Gemini (AI conversation)

**Current Phase:** Sprint 2 complete — voice calls, plan enforcement, password recovery, and dashboard stats implemented. Ready for Sprint 3 (Celery, call retry logic, payment integration).

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
```

`manage.py` loads this `.env` automatically via `python-dotenv` from `Path(__file__).resolve().parent.parent / ".env"`.

---

## Common Commands

All commands from `porvoz/` directory:

| Task | Command |
|------|---------|
| **Run dev server** | `python manage.py runserver` |
| **Apply migrations** | `python manage.py migrate` |
| **Create superuser** | `python manage.py createsuperuser` |
| **Make migrations** | `python manage.py makemigrations` |
| **Run all tests** | `python manage.py test apps` |
| **Run app tests** | `python manage.py test apps.llamadas` |
| **Check issues** | `python manage.py check` |
| **Execute pending calls (once)** | `python manage.py ejecutar_llamadas` |
| **Execute calls in loop** | `python manage.py ejecutar_llamadas --loop --intervalo 60` |

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
    │   │   ├── perfil_service.py      (Edit Perfil, change password, get_dias_restantes_plan)
    │   │   └── planes_service.py      (PlanService — limits enforcement + PLAN_LIMITS + PLANES_DATA)
    │   ├── forms.py / views.py / urls.py
    │   └── templates/usuarios/
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
    │   │   ├── detalle_paciente.html  ← Shows call badge, instructions preview, "Ver llamadas" button
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
    │   ├── models.py                  (Notificacion)
    │   ├── services/notificacion_service.py
    │   ├── forms.py / views.py / urls.py
    │   ├── templates/notificaciones/
    │   └── tests/test_services.py
    │
    └── llamadas/                      ← Sprint 2 ✓ IMPLEMENTADO
        ├── models.py                  (Llamada, RespuestaLlamada)
        ├── services/
        │   ├── llamada_service.py     (Crear, ejecutar, sanitizar, registrar, alertas)
        │   └── proveedor_voz_service.py  (Twilio + Gemini, max 2 oraciones, 280 chars)
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
| `PerfilService` | `apps.usuarios.services` | Edit Perfil, change password, dias_restantes_plan |
| `PlanService` | `apps.usuarios.services.planes_service` | Enforce plan limits, usage stats |
| `DashboardService` | `apps.dashboard.services` | Patients, call stats (7d), reminders, activity |
| `PacienteService` | `apps.pacientes.services` | Patient CRUD, phone verification |
| `MedicamentoService` | `apps.medicamentos.services` | Medication CRUD, toggle |
| `NotificacionService` | `apps.notificaciones.services` | Notification CRUD, filtering, stats |
| `LlamadaService` | `apps.llamadas.services` | Schedule, execute, sanitize, register responses |
| `ProveedorVozService` | `apps.llamadas.services` | Twilio calls + Gemini AI |
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
