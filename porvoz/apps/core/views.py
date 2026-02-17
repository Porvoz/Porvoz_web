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

        request.user.first_name = perfil.first_name
        request.user.last_name = perfil.last_name
        request.user.save()

        messages.success(request, "Perfil completado correctamente.")
        return redirect("dashboard_router")

    return render(request, "core/edit_profile.html", {"perfil": perfil})


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

