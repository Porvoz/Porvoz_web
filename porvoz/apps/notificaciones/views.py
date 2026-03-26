from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.notificaciones.models import Notificacion
from apps.notificaciones.services import NotificacionService
from apps.pacientes.models import Paciente
from apps.core.models import Perfil


def _notifications_redirect_url(request: HttpRequest) -> str:
    """Construye la URL de notificaciones preservando filtros activos."""
    source = request.POST if request.method == "POST" else request.GET
    params = {}
    t = source.get("tipo") or source.get("redirect_tipo")
    if t and t != "None":
        params["tipo"] = t
    p = source.get("paciente") or source.get("redirect_paciente")
    if p and p != "None":
        params["paciente"] = p
    if source.get("solo_no_leidas") == "1" or source.get("redirect_solo_no_leidas") == "1":
        params["solo_no_leidas"] = "1"
    b = source.get("buscar") or source.get("redirect_buscar")
    if b:
        params["buscar"] = b
    qs = urlencode(params) if params else ""
    base = reverse("notifications")
    return f"{base}?{qs}" if qs else base


@login_required
def notifications_view(request: HttpRequest) -> HttpResponse:
    """Vista para gestionar notificaciones con filtros y eliminación."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    redirect_url = _notifications_redirect_url(request)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete_selected":
            notificacion_ids = request.POST.getlist("notificacion_ids")
            if notificacion_ids:
                count = NotificacionService.eliminar_notificaciones(
                    [int(i) for i in notificacion_ids], request.user
                )
                messages.success(request, f"{count} notificación(es) eliminada(s).")
                return redirect(redirect_url)

        elif action == "delete_single":
            notificacion_id = request.POST.get("notificacion_id")
            if notificacion_id:
                if NotificacionService.eliminar_notificacion(int(notificacion_id), request.user):
                    messages.success(request, "Notificación eliminada.")
                else:
                    messages.error(request, "Notificación no encontrada.")
                return redirect(redirect_url)

        elif action == "mark_read":
            notificacion_ids = request.POST.getlist("notificacion_ids")
            if notificacion_ids:
                Notificacion.objects.filter(
                    id__in=notificacion_ids,
                    usuario=request.user,
                ).update(leida=True)
                messages.success(
                    request, f"{len(notificacion_ids)} notificación(es) marcada(s) como leída(s)."
                )
                return redirect(redirect_url)

        elif action == "mark_read_single":
            notificacion_id = request.POST.get("notificacion_id")
            if notificacion_id:
                NotificacionService.marcar_como_leida(int(notificacion_id), request.user)
                messages.success(request, "Marcada como leída.")
                return redirect(redirect_url)

        elif action == "mark_unread_single":
            notificacion_id = request.POST.get("notificacion_id")
            if notificacion_id:
                NotificacionService.marcar_como_no_leida(int(notificacion_id), request.user)
                messages.success(request, "Marcada como no leída.")
                return redirect(redirect_url)

        elif action == "mark_all_read":
            NotificacionService.marcar_todas_como_leidas(request.user)
            messages.success(request, "Todas las notificaciones marcadas como leídas.")
            params = {}
            rt = request.POST.get("redirect_tipo")
            if rt and rt != "None":
                params["tipo"] = rt
            rp = request.POST.get("redirect_paciente")
            if rp and rp != "None":
                params["paciente"] = rp
            if request.POST.get("redirect_buscar"):
                params["buscar"] = request.POST.get("redirect_buscar")
            qs = urlencode(params) if params else ""
            base = reverse("notifications")
            return redirect(f"{base}?{qs}" if qs else base)

    # Obtener filtros y aplicarlos via service (desacoplado de HttpRequest)
    datos_filtros = request.POST.dict() if request.method == "POST" else request.GET.dict()
    filtros = NotificacionService.obtener_filtros_desde_dict(datos_filtros)
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    notificaciones = NotificacionService.aplicar_filtros(notificaciones, filtros)

    notificaciones = notificaciones.select_related(
        "paciente", "paciente__usuario", "paciente__usuario__perfil", "medicamento"
    ).order_by("-creado_en")

    pacientes = (
        Paciente.objects.filter(usuario=request.user, activo=True)
        .select_related("usuario", "usuario__perfil")
        .order_by("nombre")
    )

    stats = NotificacionService.obtener_estadisticas(request.user)

    context = {
        "perfil": perfil,
        "notificaciones": notificaciones,
        "pacientes": pacientes,
        "paciente_seleccionado": filtros["paciente_id"],
        "tipo_seleccionado": filtros["tipo"],
        "fecha_desde": filtros["fecha_desde"],
        "fecha_hasta": filtros["fecha_hasta"],
        "solo_no_leidas": filtros["solo_no_leidas"],
        "buscar": filtros["buscar"],
        "total_notificaciones": stats["total"],
        "no_leidas": stats["no_leidas"],
        "total_recordatorios": stats["total_recordatorios"],
        "total_alertas": stats["total_alertas"],
        "tipos": Notificacion.TIPO_CHOICES,
    }
    return render(request, "notificaciones/notifications.html", context)
