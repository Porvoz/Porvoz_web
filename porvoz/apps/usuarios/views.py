from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.core.models import Perfil
from apps.shared.services import TelefonoService, obtener_planes
from apps.usuarios.services import PerfilService


@login_required
def complete_profile_view(request: HttpRequest) -> HttpResponse:
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    editando = request.GET.get("edit") == "1"
    tab_activo = request.GET.get("tab", "perfil")

    # Manejar cambio de plan
    if request.method == "POST" and request.POST.get("action") == "cambiar_plan":
        nuevo_plan = request.POST.get("plan", "").strip()
        success, error_msg = PerfilService.cambiar_plan(perfil, nuevo_plan)
        if success:
            messages.success(request, f"Plan actualizado a {perfil.get_plan_display()}.")
            return redirect(f"{reverse('edit_profile')}?tab=planes")
        else:
            messages.error(request, error_msg)
            return redirect(f"{reverse('edit_profile')}?tab=planes")

    # Manejar actualización de perfil
    if request.method == "POST" and request.POST.get("action") != "cambiar_plan":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        city = request.POST.get("city", "").strip()
        phone_country = request.POST.get("phone_country", "+57").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        document_type = request.POST.get("document_type", "").strip()
        document_number = request.POST.get("document_number", "").strip()
        date_of_birth_str = request.POST.get("date_of_birth", "").strip()
        emergency_contact_name = request.POST.get("emergency_contact_name", "").strip()
        emergency_country = request.POST.get("emergency_contact_phone_country", "+57").strip()
        emergency_number = request.POST.get("emergency_contact_phone_number", "").strip()
        profile_image = request.FILES.get("profile_image")

        success, error_msg = PerfilService.actualizar_perfil(
            perfil,
            first_name=first_name,
            last_name=last_name,
            city=city,
            phone_country=phone_country,
            phone_number=phone_number,
            document_type=document_type,
            document_number=document_number,
            date_of_birth_str=date_of_birth_str,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone_country=emergency_country,
            emergency_contact_phone_number=emergency_number,
            profile_image=profile_image,
        )

        if success:
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect(f"{reverse('edit_profile')}?tab=perfil")
        else:
            messages.error(request, error_msg)
            return redirect(f"{reverse('edit_profile')}?tab=perfil&edit=1")

    # Preparar contexto para mostrar en GET
    first_name = perfil.first_name or request.user.first_name or ""
    last_name = perfil.last_name or request.user.last_name or ""

    phone_parsed = TelefonoService.parsear_telefono(perfil.phone)
    phone_country = phone_parsed.pais
    phone_number = phone_parsed.numero

    emergency_parsed = TelefonoService.parsear_telefono(perfil.emergency_contact_phone)
    emergency_phone_country = emergency_parsed.pais
    emergency_phone_number = emergency_parsed.numero

    planes = obtener_planes(plan_actual=perfil.plan)

    context = {
        "perfil": perfil,
        "first_name": first_name,
        "last_name": last_name,
        "phone_country": phone_country,
        "phone_number": phone_number,
        "emergency_phone_country": emergency_phone_country,
        "emergency_phone_number": emergency_phone_number,
        "editando": editando,
        "tab_activo": tab_activo,
        "planes": planes,
    }
    return render(request, "usuarios/edit_profile.html", context)


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
            messages.success(
                request,
                "Contraseña actualizada correctamente. Por favor, inicia sesión nuevamente.",
            )
            return redirect("login")

    return render(request, "usuarios/change_password.html", {"perfil": perfil})


def plans_view(request: HttpRequest) -> HttpResponse:
    """Vista para mostrar los planes (invitados). Logueados van a Mi cuenta > Plan."""
    if request.user.is_authenticated:
        return redirect(f"{reverse('edit_profile')}?tab=planes")

    context = {
        "perfil": None,
        "planes": obtener_planes(),
        "plan_actual": None,
    }
    return render(request, "usuarios/plans.html", context)
