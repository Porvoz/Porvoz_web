import logging

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django_ratelimit.decorators import ratelimit

from apps.autenticacion.services import RegistroService
from apps.usuarios.services import PerfilService

logger = logging.getLogger(__name__)
User = get_user_model()


@never_cache
@ratelimit(key="ip", rate="5/15m", method="POST", block=False)
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard_router")

    if request.method == "POST":
        if getattr(request, "limited", False):
            messages.error(
                request,
                "Demasiados intentos fallidos. Espera 15 minutos antes de intentar de nuevo.",
            )
            return render(request, "autenticacion/login.html")

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        if not username or not password:
            messages.error(request, "Por favor ingresa tu usuario y contraseña.")
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard_router")
            logger.warning("login_failed username=%s ip=%s", username, request.META.get("REMOTE_ADDR"))
            messages.error(
                request,
                "Usuario o contraseña incorrectos. Verifica los datos e intenta de nuevo.",
            )

    return render(request, "autenticacion/login.html")


@login_required
def delete_account_view(request: HttpRequest) -> HttpResponse:
    """Eliminación de cuenta en 2 pasos — cumple ARCC Ley 1581."""
    if request.method == "POST":
        confirm = request.POST.get("confirm_text", "").strip()
        if confirm != "ELIMINAR":
            messages.error(request, "Debes escribir exactamente: ELIMINAR")
            return render(request, "autenticacion/delete_account.html")
        user = request.user
        logger.info("account_deleted username=%s", user.username)
        # Anonimizar llamadas antes de borrar
        from apps.llamadas.models import Llamada
        Llamada.objects.filter(usuario=user).update(usuario=None)
        logout(request)
        user.delete()
        messages.success(request, "Tu cuenta fue eliminada. Lamentamos verte partir.")
        return redirect("login")
    return render(request, "autenticacion/delete_account.html")


@never_cache
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
        emergency_contact_phone_country = request.POST.get(
            "emergency_contact_phone_country", "+57"
        ).strip()
        emergency_contact_phone_number = request.POST.get(
            "emergency_contact_phone_number", ""
        ).strip()

        # Validaciones básicas
        if not username or not email or not password or not first_name or not last_name:
            messages.error(request, "Por favor completa todos los campos obligatorios.")
        elif password != password2:
            messages.error(request, "Las contraseñas no coinciden. Verifica e intenta de nuevo.")
        elif len(password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Ese nombre de usuario ya está registrado. Prueba con otro.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Ese correo ya tiene una cuenta. ¿Quieres iniciar sesión?")
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
                messages.success(
                    request, "Cuenta creada. Inicia sesión para continuar."
                )
                return redirect("login")
            except Exception:
                logger.exception("Error al registrar usuario %s", username)
                messages.error(
                    request,
                    "No pudimos crear tu cuenta en este momento. "
                    "Verifica tus datos e intenta de nuevo en unos segundos.",
                )

    return render(request, "autenticacion/register.html")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")


