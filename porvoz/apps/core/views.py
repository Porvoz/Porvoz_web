from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .models import Perfil


VALID_ROLES = {Perfil.ROLE_PATIENT, Perfil.ROLE_CAREGIVER}


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

    return render(request, "core/login.html")


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
        role = request.POST.get("role")
        phone_country = request.POST.get("phone_country", "+57").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        document_type = request.POST.get("document_type", "").strip()
        document_number = request.POST.get("document_number", "").strip()
        date_of_birth = request.POST.get("date_of_birth", "").strip()
        city = request.POST.get("city", "").strip()
        emergency_contact_name = request.POST.get("emergency_contact_name", "").strip()
        emergency_contact_phone_country = request.POST.get("emergency_contact_phone_country", "+57").strip()
        emergency_contact_phone_number = request.POST.get("emergency_contact_phone_number", "").strip()

        if not username or not email or not password or not first_name or not last_name:
            messages.error(request, "Todos los campos son obligatorios.")
        elif password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif role not in {Perfil.ROLE_PATIENT, Perfil.ROLE_CAREGIVER}:
            messages.error(request, "Selecciona un rol válido.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save(update_fields=["first_name", "last_name"])

            full_phone = f"{phone_country} {phone_number}".strip()
            emergency_phone = f"{emergency_contact_phone_country} {emergency_contact_phone_number}".strip()
            Perfil.objects.create(
                user=user,
                role=role,
                first_name=first_name,
                last_name=last_name,
                phone=full_phone,
                document_type=document_type,
                document_number=document_number,
                date_of_birth=date_of_birth or None,
                city=city,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_phone=emergency_phone,
                profile_completed=True,
            )
            messages.success(request, "Cuenta creada. Inicia sesión para continuar.")
            return redirect("login")

    return render(request, "core/register.html")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")


@login_required
def dashboard_router(request: HttpRequest) -> HttpResponse:
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    if perfil.role not in VALID_ROLES:
        # Avoid redirect loops for legacy users with empty/invalid role.
        perfil.role = Perfil.ROLE_PATIENT
        perfil.save(update_fields=["role"])
    if perfil.role == Perfil.ROLE_CAREGIVER:
        return redirect("dashboard")
    return redirect("patient_dashboard")


@login_required
def complete_profile_view(request: HttpRequest) -> HttpResponse:
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == "POST":
        perfil.first_name = request.POST.get("first_name", "").strip()
        perfil.last_name = request.POST.get("last_name", "").strip()
        perfil.city = request.POST.get("city", "").strip()
        phone_country = request.POST.get("phone_country", "+57").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        perfil.phone = f"{phone_country} {phone_number}".strip()
        perfil.document_type = request.POST.get("document_type", "").strip()
        perfil.document_number = request.POST.get("document_number", "").strip()
        perfil.date_of_birth = request.POST.get("date_of_birth", "").strip() or None
        perfil.emergency_contact_name = request.POST.get("emergency_contact_name", "").strip()
        emergency_country = request.POST.get("emergency_contact_phone_country", "+57").strip()
        emergency_number = request.POST.get("emergency_contact_phone_number", "").strip()
        perfil.emergency_contact_phone = f"{emergency_country} {emergency_number}".strip()
        profile_image = request.FILES.get("profile_image")
        if profile_image:
            perfil.profile_image = profile_image
        perfil.profile_completed = True
        perfil.save()

        request.user.first_name = perfil.first_name or request.user.first_name
        request.user.last_name = perfil.last_name or request.user.last_name
        request.user.save()

        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("dashboard_router")

    # Usar datos del perfil, o del User si el perfil no los tiene
    first_name = perfil.first_name or request.user.first_name or ""
    last_name = perfil.last_name or request.user.last_name or ""
    
    # Parsear teléfonos para mostrar en el formulario
    phone_country = "+57"
    phone_number = ""
    if perfil.phone:
        parts = perfil.phone.split(" ", 1)
        if len(parts) == 2:
            phone_country = parts[0]
            phone_number = parts[1]
        elif perfil.phone.startswith("+"):
            phone_country = perfil.phone[:3] if len(perfil.phone) >= 3 else "+57"
            phone_number = perfil.phone[3:].strip()

    emergency_phone_country = "+57"
    emergency_phone_number = ""
    if perfil.emergency_contact_phone:
        parts = perfil.emergency_contact_phone.split(" ", 1)
        if len(parts) == 2:
            emergency_phone_country = parts[0]
            emergency_phone_number = parts[1]
        elif perfil.emergency_contact_phone.startswith("+"):
            emergency_phone_country = perfil.emergency_contact_phone[:3] if len(perfil.emergency_contact_phone) >= 3 else "+57"
            emergency_phone_number = perfil.emergency_contact_phone[3:].strip()

    context = {
        "perfil": perfil,
        "first_name": first_name,
        "last_name": last_name,
        "phone_country": phone_country,
        "phone_number": phone_number,
        "emergency_phone_country": emergency_phone_country,
        "emergency_phone_number": emergency_phone_number,
    }
    return render(request, "core/edit_profile.html", context)


@login_required
def caregiver_dashboard(request: HttpRequest) -> HttpResponse:
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    if perfil.role != Perfil.ROLE_CAREGIVER:
        return redirect("dashboard_router")
    return render(request, "core/dashboard.html", {"perfil": perfil})


@login_required
def patient_dashboard(request: HttpRequest) -> HttpResponse:
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    if perfil.role != Perfil.ROLE_PATIENT:
        return redirect("dashboard_router")
    return render(request, "core/patient_dashboard.html", {"perfil": perfil})


@login_required
def medical_data_view(request: HttpRequest) -> HttpResponse:
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    if perfil.role != Perfil.ROLE_PATIENT:
        return redirect("dashboard")
    return render(request, "core/medical_data.html", {"perfil": perfil})


@login_required
def notifications_view(request: HttpRequest) -> HttpResponse:
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    return render(request, "core/notifications.html", {"perfil": perfil})


@login_required
def caregiver_patients_view(request: HttpRequest) -> HttpResponse:
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    if perfil.role != Perfil.ROLE_CAREGIVER:
        return redirect("patient_dashboard")
    return render(request, "core/caregiver_patients.html", {"perfil": perfil})


@login_required
def change_password_view(request: HttpRequest) -> HttpResponse:
    """Vista para cambiar la contraseña del usuario."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == "POST":
        old_password = request.POST.get("old_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not old_password or not new_password or not confirm_password:
            messages.error(request, "Todos los campos son obligatorios.")
        elif not request.user.check_password(old_password):
            messages.error(request, "La contraseña actual es incorrecta.")
        elif len(new_password) < 8:
            messages.error(request, "La nueva contraseña debe tener al menos 8 caracteres.")
        elif new_password != confirm_password:
            messages.error(request, "Las nuevas contraseñas no coinciden.")
        elif old_password == new_password:
            messages.error(request, "La nueva contraseña debe ser diferente a la actual.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "Contraseña actualizada correctamente. Por favor, inicia sesión nuevamente.")
            return redirect("login")

    return render(request, "core/change_password.html", {"perfil": perfil})


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
            from django.contrib.auth.models import User
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
                    f"Por favor revisa tu correo electrónico. (Funcionalidad en desarrollo)"
                )
            except User.DoesNotExist:
                # Por seguridad, no revelamos si el usuario existe o no
                messages.success(
                    request,
                    "Si existe una cuenta con ese usuario o correo, se ha enviado un enlace de recuperación. "
                    "Por favor revisa tu correo electrónico. (Funcionalidad en desarrollo)"
                )

    return render(request, "core/reset_password.html")

