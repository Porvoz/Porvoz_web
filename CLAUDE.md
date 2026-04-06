# CLAUDE.md

This file provides guidance to Claude Code when working with the Porvoz project.

## Project Overview

**Porvoz** is a Django web application for managing medication reminders using automated voice calls. Caregivers register medications with dosing schedules and health conditions. The system sends automated reminders via voice calls, registers confirmations, and alerts when medications are not taken.

**Tech Stack:** Django 5.2, Django REST Framework, SQLite (dev), Tailwind CSS, Bootstrap Icons, Twilio (voice calls), Google Gemini (AI conversation)

**Current Phase:** Sprint 2 complete — voice calls implemented. Ready for Sprint 3 (Celery, multi-schedule UI, call retry logic).

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

Create `.env` file at repo root (never commit this):
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_BASE_URL=https://your-ngrok-or-domain.com
DJANGO_SECRET_KEY=your-secret-key-here
```

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
│   ├── settings/base.py               ← DIRS: ["BASE_DIR / templates"]
│   ├── urls.py                        ← Includes all apps
│   └── wsgi.py
│
└── apps/
    ├── core/                          ← Core layer: ONLY models + utils
    │   ├── models.py                  (Perfil extends User)
    │   ├── context_processors.py      (perfil_sidebar)
    │   └── apps.py
    │
    ├── shared/                        ← Cross-cutting utilities
    │   ├── services/
    │   │   ├── telefono_service.py    (Parse, format, sanitize phones)
    │   │   └── planes_service.py      (Static plan data)
    │   ├── exceptions.py              (PacienteError, MedicamentoError, etc.)
    │   └── apps.py
    │
    ├── PRESENTATION APPS ─────────────────────────────
    │
    ├── autenticacion/
    │   ├── services/registro_service.py
    │   ├── forms.py / views.py / urls.py
    │   └── templates/autenticacion/
    │
    ├── usuarios/
    │   ├── services/perfil_service.py
    │   ├── forms.py / views.py / urls.py
    │   └── templates/usuarios/
    │
    ├── dashboard/
    │   ├── services/dashboard_service.py
    │   ├── views.py / urls.py
    │   └── templates/dashboard/
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
    │   └── tests/test_services.py
    │
    ├── medicamentos/
    │   ├── models.py                  (Medicamento, HorarioMedicamento)
    │   ├── services/medicamento_service.py
    │   ├── forms.py / views.py / urls.py
    │   ├── templates/medicamentos/
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
        │   ├── llamada_service.py     (Crear, ejecutar, registrar respuesta, alertas)
        │   └── proveedor_voz_service.py  (Twilio + Gemini)
        ├── forms.py                   (FiltroHistorialLlamadasForm)
        ├── views.py                   (historial_llamadas, webhook_voice/gather/status)
        ├── urls.py
        ├── templates/llamadas/
        │   └── historial.html
        ├── management/
        │   └── commands/
        │       └── ejecutar_llamadas.py  (--loop para modo continuo)
        ├── migrations/
        │   ├── 0001_initial.py        (Notificacion — histórico, movida a notificaciones)
        │   ├── 0002_rename_...        (rename indexes)
        │   ├── 0003_remove_...        (SeparateDatabaseAndState)
        │   └── 0004_add_llamada_respuesta.py  ← modelos actuales
        ├── tests/test_services.py
        └── apps.py
```

---

## Core Concepts

### User Model
- Only 1 type of user: "Cuidador" (self-caregiver or caregiver for others)
- Extended via `Perfil` (1:1 with User)
- Has plans (freemium, growth, multi-cuidador) with expiration

### Data Relationships
```
User (Django)
  └─ Perfil (1:1)
     ├─ Pacientes (1:N)
     │  ├─ Medicamentos (1:N)
     │  │  ├─ HorarioMedicamento (1:N - multiple times per day)
     │  │  ├─ instrucciones_llamada  ← contexto para la IA
     │  │  ├─ minutos_antes_llamada  ← offset para programar llamada
     │  │  └─ Llamadas (1:N)
     │  │     └─ RespuestaLlamada (1:1)
     │  ├─ Enfermedades (1:N)
     │  └─ Notificaciones (1:N)
     └─ Notificaciones (1:N - alertas, recordatorios, sistema)
```

### Notification Types
- `TIPO_SISTEMA` — System events (patient added, medication created)
- `TIPO_RECORDATORIO` — Internal reminders (display only)
- `TIPO_ALERTA` — Alerts (call not answered, error)

### Call States
```
Llamada.estado:
  programada → en_curso → completada
                        ↘ fallida

RespuestaLlamada.como_respondio:
  atendida | no_atendida | buzon
  (no_atendida / buzon → crea Notificacion TIPO_ALERTA automáticamente)
```

### Service Organization

| Service | Location | Responsibility |
|---------|----------|-----------------|
| `RegistroService` | `apps.autenticacion.services` | Create User + Perfil |
| `PerfilService` | `apps.usuarios.services` | Edit Perfil, change password, plans |
| `DashboardService` | `apps.dashboard.services` | Fetch patients, stats, sorting |
| `PacienteService` | `apps.pacientes.services` | Patient CRUD, phone verification |
| `MedicamentoService` | `apps.medicamentos.services` | Medication CRUD, toggle |
| `NotificacionService` | `apps.notificaciones.services` | Notification CRUD, filtering, stats |
| `LlamadaService` | `apps.llamadas.services` | Schedule, execute, register responses |
| `ProveedorVozService` | `apps.llamadas.services` | Twilio calls + Gemini AI |
| `TelefonoService` | `apps.shared.services` | Parse, format, sanitize phones |
| `obtener_planes` | `apps.shared.services` | Static plan data |

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
4. Use exceptions from `apps.shared.exceptions`

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
            except MyError as e:
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

## Testing

```bash
python manage.py test apps                  # All tests (54)
python manage.py test apps.llamadas         # 7 tests
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
- **Models:** Spanish field labels, Meta class with db_table
- **Services:** `@staticmethod`, HTTP-agnostic, return tuples or data
- **Exceptions:** Use `apps.shared.exceptions` custom exceptions
- **Naming:** `_` prefix for private functions, `get_` for getters, `create_/update_/delete_` for mutations

---

## Templates

- **Global templates:** `templates/` (base.html, sidebar.html, footer.html)
- **App templates:** `apps/<app>/templates/<app>/`
- **Styling:** Tailwind CSS utility classes (responsive by default)
- **Icons:** Bootstrap Icons (SVG, scalable)
- **Design tokens:** `bg-slate-100`, `rounded-2xl`, `border-l-4`, `shadow-sm`, `font-black`

---

## Voice Calls — Sprint 2 Implementation

### Flow

```
Medicamento (instrucciones_llamada + minutos_antes_llamada)
  ↓
LlamadaService.crear_llamada_programada()
  ↓
python manage.py ejecutar_llamadas [--loop]
  ↓
LlamadaService.ejecutar_llamadas_pendientes()
  ↓
ProveedorVozService.disparar_llamada(numero, mensaje, voice_url, status_url)
  ↓
Twilio → POST /llamadas/webhook/voice/?llamada_id=X&mensaje=...
  ↓
ProveedorVozService.generar_respuesta_ia()  ← Gemini
  ↓
Twilio → POST /llamadas/webhook/gather/  (cada turno de conversación)
  ↓
Twilio → POST /llamadas/webhook/status/  (fin de llamada)
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
| `TWILIO_PHONE_NUMBER` | Twilio number in E.164 format (+1xxxxxxxxxx) |
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
- Webhooks: Twilio sends POST without CSRF token → use `@csrf_exempt` only on webhook views
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
- **Call history filters:** Date range filter in historial view
- **Twilio signature validation:** Verify webhook authenticity (`X-Twilio-Signature`)
- **Conversation persistence:** Store `_conversaciones` in Django cache / Redis

---

## Removed/Deprecated

- ❌ `apps.recordatorios` — Moved to `Notificacion.TIPO_RECORDATORIO` + llamadas automáticas
- ❌ `apps.cuidadores` — No RBAC; "cuidador" is just User with Perfil
- ❌ External apps (`calls/`, `contacts/`, `reminders/`, `ai/`) — Prototype by teammate, not used; logic was adapted into `apps.llamadas`
