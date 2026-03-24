from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.autenticacion.services import RegistroService
from apps.usuarios.services import PerfilService


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard_router")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard_router")
        messages.error(request, "Credenciales inválidas.")

    return render(request, "autenticacion/login.html")


def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard_router")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        phone_country = request.POST.get("phone_country", "+57").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        document_type = request.POST.get("document_type", "").strip()
        document_number = request.POST.get("document_number", "").strip()
        date_of_birth = request.POST.get("date_of_birth", "").strip()
        city = request.POST.get("city", "").strip()
        emergency_contact_name = request.POST.get("emergency_contact_name", "").strip()
        emergency_contact_phone_country = request.POST.get("emergency_contact_phone_country", "+57").strip()
        emergency_contact_phone_number = request.POST.get("emergency_contact_phone_number", "").strip()

        # Validaciones básicas
        if not username or not email or not password or not first_name or not last_name:
            messages.error(request, "Todos los campos son obligatorios.")
        elif password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
        else:
            # Validar edad si se proporciona fecha de nacimiento
            birth_date_obj = None
            if date_of_birth:
                birth_date_obj, error_msg = PerfilService.validar_edad(date_of_birth)
                if error_msg:
                    messages.error(request, error_msg)
                    return render(request, "autenticacion/register.html")

            # Crear usuario y perfil usando service
            try:
                RegistroService.crear_usuario_y_perfil(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_country=phone_country,
                    phone_number=phone_number,
                    document_type=document_type,
                    document_number=document_number,
                    date_of_birth=birth_date_obj,
                    city=city,
                    emergency_contact_name=emergency_contact_name,
                    emergency_contact_phone_country=emergency_contact_phone_country,
                    emergency_contact_phone_number=emergency_contact_phone_number,
                )
                messages.success(request, "Cuenta creada. Inicia sesión para continuar.")
                return redirect("login")
            except Exception as e:
                messages.error(request, f"Error al crear la cuenta: {str(e)}")

    return render(request, "autenticacion/register.html")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")


def reset_password_view(request: HttpRequest) -> HttpResponse:
    """Vista para solicitar recuperación de contraseña."""
    if request.user.is_authenticated:
        return redirect("dashboard_router")

    if request.method == "POST":
        username_or_email = request.POST.get("username_or_email", "").strip()

        if not username_or_email:
            messages.error(request, "Por favor ingresa tu usuario o correo electrónico.")
        else:
            # Buscar usuario por username o email
            try:
                if "@" in username_or_email:
                    user = User.objects.get(email=username_or_email)
                else:
                    user = User.objects.get(username=username_or_email)

                # Aquí iría la lógica para enviar el email de recuperación
                # Por ahora solo mostramos un mensaje de éxito
                messages.success(
                    request,
                    f"Si existe una cuenta con ese usuario o correo, se ha enviado un enlace de recuperación. "
                    f"Por favor revisa tu correo electrónico. (Funcionalidad en desarrollo)",
                )
            except User.DoesNotExist:
                # Por seguridad, no revelamos si el usuario existe o no
                messages.success(
                    request,
                    "Si existe una cuenta con ese usuario o correo, se ha enviado un enlace de recuperación. "
                    "Por favor revisa tu correo electrónico. (Funcionalidad en desarrollo)",
                )

    return render(request, "autenticacion/reset_password.html")
