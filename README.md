# Porvoz

Porvoz es una aplicación web para la gestión de recordatorios de medicamentos. Permite a cuidadores y pacientes registrar medicamentos, horarios de toma y condiciones de salud, con un dashboard unificado, sistema de notificaciones y preparación para llamadas automatizadas.

---

## Cómo ejecutar el proyecto

1. Clonar el repositorio y entrar a la carpeta del proyecto (donde está `manage.py`).

2. Crear y activar el entorno virtual:

   * **Windows:**

     ```
     venv\Scripts\activate
     ```

   * **Linux/macOS:**

     ```
     source venv/bin/activate
     ```

3. Instalar dependencias:

   ```
   pip install -r requirements.txt
   ```

4. Aplicar migraciones:

   ```
   python manage.py migrate
   ```

5. (Opcional) Crear superusuario:

   ```
   python manage.py createsuperuser
   ```

6. Levantar el servidor:

   ```
   python manage.py runserver
   ```

---

## Tecnologías utilizadas

* **Backend:** Django 5.x, Django REST Framework
* **Frontend:** HTML, Tailwind CSS, Bootstrap Icons
* **Base de datos:** SQLite (entorno de desarrollo)
* **Autenticación:** Django Auth
* **Control de versiones:** Git / GitHub

---

## Estructura del proyecto

```
proyecto 2/
├── porvoz/
│   ├── apps/
│   │   ├── core/           # Autenticación, perfil, dashboard, notificaciones, legal
│   │   ├── cuidadores/     # Gestión de cuidadores
│   │   ├── pacientes/      # Pacientes y condiciones
│   │   ├── medicamentos/   # Medicamentos y horarios
│   │   ├── recordatorios/  # Sistema de recordatorios
│   │   └── llamadas/       # Llamadas automatizadas
│   ├── config/             # Settings Django, urls, wsgi
│   ├── static/
│   ├── media/
│   ├── manage.py
│   └── requirements.txt
└── venv/
```

---

## Integrantes del equipo

* Luis Alfonso Agudelo Ramírez
* Julián Lara Aristizabal
* Matías Martínez Moreno
* Nathalia Cardoza
* Samuel Samper

---

## Product Owners

* Mateo Zacar
* Styven Bedoya
