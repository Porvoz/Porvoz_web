# Porvoz

Porvoz es un sistema de recordatorios de medicamentos que llama por teléfono a pacientes cronicamente enfermos para asegurar adherencia terapéutica. El cuidador registra pacientes y medicamentos una sola vez. El sistema llama automáticamente a la hora programada, reproduce un saludo personalizado, detecta mediante IA si el paciente tomó el medicamento, y notifica al cuidador de cualquier incumplimiento para que intervenga inmediatamente.

**Aplicación en vivo:** http://34.198.74.65

## Equipo

- Luis Alfonso Agudelo Ramírez
- Julián Lara Aristizabal
- Matías Martínez Moreno
- Nathalia Cardoza
- Samuel Samper

**Product Owners:** Mateo Zacar · Styven Bedoya

---

## Stack

- **Backend:** Django 5.2 + Gunicorn
- **Llamadas de voz:** Twilio
- **Clasificación de respuestas:** Google Gemini AI
- **Frontend:** HTML + Tailwind CSS + Bootstrap Icons
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Cache y tareas async:** Redis + Celery
- **CI:** GitHub Actions — tests en cada PR
