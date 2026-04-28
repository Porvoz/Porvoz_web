# Porvoz

Plataforma que llama por teléfono a pacientes para recordarles sus medicamentos. El cuidador configura una vez; el sistema llama solo, detecta si el paciente tomó el medicamento y avisa cuando algo sale mal.

## Equipo

- Luis Alfonso Agudelo Ramírez
- Julián Lara Aristizabal
- Matías Martínez Moreno
- Nathalia Cardoza
- Samuel Samper

**Product Owners:** Mateo Zacar · Styven Bedoya

---

## Cómo correr el proyecto

Se necesitan **tres terminales** abiertas al mismo tiempo.

### Terminal 1 — Servidor Django
```bash
cd porvoz
python manage.py runserver
```

### Terminal 2 — Ngrok (expone el servidor a Twilio)
```bash
python scripts/ngrok_run.py
```
Copia la URL `https://xxxx.ngrok.io` que imprime y pégala en `porvoz/.env` como `TWILIO_BASE_URL`. Reinicia la Terminal 1 después de hacerlo.

### Terminal 3 — Scheduler de llamadas (cada 60 segundos)
```bash
cd porvoz
python manage.py ejecutar_llamadas --loop --intervalo 60
```

---

## Stack

- **Backend:** Django 5.2
- **Llamadas de voz:** Twilio
- **Clasificación de respuestas:** Google Gemini AI
- **Frontend:** HTML + Tailwind CSS + Bootstrap Icons
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **CI:** GitHub Actions — tests + coverage + ruff en cada PR
