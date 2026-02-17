# Porvoz - Sistema de Recordatorios de Medicamentos

Sistema web profesional para gestión de recordatorios de medicamentos mediante llamadas automatizadas, diseñado para cuidadores y pacientes.

## 🏗️ Estructura del Proyecto

```
proyecto 2/
├── porvoz/                    # Django project
│   ├── apps/                  # Microapps
│   │   ├── porvoz/           # Core: autenticación, perfiles, dashboards
│   │   ├── cuidadores/       # Gestión de cuidadores
│   │   ├── pacientes/        # Gestión de pacientes
│   │   ├── medicamentos/     # Gestión de medicamentos
│   │   ├── recordatorios/    # Sistema de recordatorios
│   │   └── llamadas/         # Sistema de llamadas automatizadas
│   ├── config/               # Configuración Django
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   └── development.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── static/               # Archivos estáticos (CSS, JS, imágenes)
│   ├── media/                # Archivos subidos por usuarios
│   ├── manage.py
│   └── requirements.txt
└── venv/                     # Entorno virtual (no se sube a Git)
```

## 🚀 Instalación y Configuración

### 1. Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
cd porvoz
pip install -r requirements.txt
```

### 3. Ejecutar migraciones

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 4. Crear superusuario (opcional)

```powershell
python manage.py createsuperuser
```

### 5. Ejecutar el servidor

```powershell
python manage.py runserver
```

El proyecto estará disponible en: `http://127.0.0.1:8000/`

## 🎨 Tecnologías

- **Backend**: Django 5.2
- **Frontend**: Tailwind CSS
- **Base de datos**: SQLite (desarrollo)
- **Autenticación**: Django Auth
- **APIs**: Django REST Framework

## 📱 Flujo de Usuario

1. **Registro**: El usuario se registra eligiendo su rol (Paciente o Cuidador)
2. **Login**: Inicia sesión con sus credenciales
3. **Completar perfil**: Completa información personal (nombre, ciudad, teléfono)
4. **Dashboard**: Accede a su panel según su rol
   - **Cuidadores**: Gestión de pacientes, medicamentos y recordatorios
   - **Pacientes**: Visualización de medicamentos y recordatorios

## 🔧 Comandos Útiles

```powershell
# Crear una nueva migración
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver

# Recolectar archivos estáticos
python manage.py collectstatic
```

## 📝 Notas

- El proyecto usa una arquitectura de **microapps** para mejor organización
- Cada app tiene su propia responsabilidad y puede desarrollarse independientemente
- Los templates usan **Tailwind CSS** para un diseño moderno y profesional
- El sidebar es **plegable** y guarda su estado en localStorage

