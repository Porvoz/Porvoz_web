"""
Vistas principales de la webapp Porvoz.

Incluye:
- Flujo de autenticación básico (login, registro, logout)
- Dashboard principal con sidebar moderno (prototipo)
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import Perfil


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Primera pantalla de la webapp.
    Si el usuario ya está autenticado, se redirige según su rol.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("dashboard")
        return redirect("patient_dashboard")

    if request.method == "POST":
        email_or_username = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=email_or_username, password=password)
        if user is None:
            # Intento adicional: buscar por email y autenticar por username
            from django.contrib.auth.models import User

            try:
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            # Redirección según tipo de usuario
            if user.is_staff:
                return redirect("dashboard")
            return redirect("patient_dashboard")

        messages.error(
            request,
            "Credenciales inválidas. Verifica tu correo/usuario y contraseña.",
        )

    return render(request, "porvoz/login.html")


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Registro básico de usuarios (cuidadores y pacientes) usando el modelo User de Django.
    Los cuidadores se marcan como is_staff para diferenciarlos de los pacientes.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("dashboard")
        return redirect("patient_dashboard")

    if request.method == "POST":
        from django.contrib.auth.models import User

        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        password_confirm = request.POST.get("password_confirm", "").strip()
        role = request.POST.get("role", "caregiver")
        phone = request.POST.get("phone", "").strip()
        age_raw = request.POST.get("age", "").strip()
        address = request.POST.get("address", "").strip()

        # Validaciones básicas de formulario
        if not all([full_name, email, password, phone, age_raw, address]):
            messages.error(request, "Todos los campos son obligatorios.")
        elif password != password_confirm:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            try:
                age = int(age_raw)
                if age < 0:
                    raise ValueError
            except ValueError:
                messages.error(request, "La edad debe ser un número válido.")
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, "Ya existe un usuario registrado con este correo.")
                else:
                    username = email  # Para simplificar, usamos el email como username
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=full_name,
                    )
                    # Marcamos a los cuidadores como usuarios de staff
                    if role == "caregiver":
                        user.is_staff = True
                        user.save(update_fields=["is_staff"])

                    # Creamos el perfil con la información adicional
                    Perfil.objects.create(
                        user=user,
                        phone=phone,
                        age=age,
                        address=address,
                        role=role,
                    )

                    login(request, user)
                    if user.is_staff:
                        return redirect("dashboard")
                    return redirect("patient_dashboard")

    return render(request, "porvoz/register.html")


@login_required
def logout_view(request):
    """
    Cierre de sesión y redirección al login.
    """
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    """
    Dashboard principal con sidebar.
    De momento muestra datos estáticos a modo de prototipo.
    """
    # Si es paciente, lo redirigimos a su propio dashboard
    if not request.user.is_staff:
        return redirect("patient_dashboard")

    context = {
        "user_name": request.user.first_name or request.user.username,
        "active_patients": 2,
        "active_medications": 5,
        "today_reminders": 3,
    }
    return render(request, "porvoz/dashboard.html", context)


@login_required
def patient_dashboard(request):
    """
    Dashboard simple para pacientes.
    Más adelante se conectará con sus medicamentos y recordatorios.
    """
    context = {
        "user_name": request.user.first_name or request.user.username,
    }
    return render(request, "porvoz/patient_dashboard.html", context)

