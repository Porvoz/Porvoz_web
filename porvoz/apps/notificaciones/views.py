from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.core.models import Perfil
from apps.notificaciones.models import Notificacion
from apps.notificaciones.services import NotificacionService
from apps.pacientes.models import Paciente


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
    if (
        source.get("solo_no_leidas") == "1"
        or source.get("redirect_solo_no_leidas") == "1"
    ):
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
                if NotificacionService.eliminar_notificacion(
                    int(notificacion_id), request.user
                ):
                    messages.success(request, "Notificación eliminada.")
                else:
                    messages.error(request, "Notificación no encontrada.")
                return redirect(redirect_url)

        elif action == "mark_read":
            notificacion_ids = request.POST.getlist("notificacion_ids")
            if notificacion_ids:
                count = NotificacionService.marcar_notificaciones_como_leidas(
                    [int(i) for i in notificacion_ids], request.user
                )
                messages.success(
                    request,
                    f"{count} notificación(es) marcada(s) como leída(s).",
                )
                return redirect(redirect_url)

        elif action == "mark_read_single":
            notificacion_id = request.POST.get("notificacion_id")
            if notificacion_id:
                NotificacionService.marcar_como_leida(
                    int(notificacion_id), request.user
                )
                messages.success(request, "Marcada como leída.")
                return redirect(redirect_url)

        elif action == "mark_unread_single":
            notificacion_id = request.POST.get("notificacion_id")
            if notificacion_id:
                NotificacionService.marcar_como_no_leida(
                    int(notificacion_id), request.user
                )
                messages.success(request, "Marcada como no leída.")
                return redirect(redirect_url)

        elif action == "mark_all_read":
            NotificacionService.marcar_todas_como_leidas(request.user)
            messages.success(request, "Todas las notificaciones marcadas como leídas.")
            return redirect(redirect_url)

    # Obtener filtros y aplicarlos via service (desacoplado de HttpRequest)
    datos_filtros = (
        request.POST.dict() if request.method == "POST" else request.GET.dict()
    )
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

    # Resolver nombre del medicamento filtrado para mostrarlo en el pill
    medicamento_seleccionado = filtros.get("medicamento_id")
    medicamento_nombre = None
    if medicamento_seleccionado:
        from apps.medicamentos.models import Medicamento
        med_obj = Medicamento.objects.filter(
            id=medicamento_seleccionado, paciente__usuario=request.user
        ).first()
        medicamento_nombre = med_obj.nombre if med_obj else None

    context = {
        "perfil": perfil,
        "notificaciones": notificaciones,
        "pacientes": pacientes,
        "paciente_seleccionado": filtros["paciente_id"],
        "medicamento_seleccionado": medicamento_seleccionado,
        "medicamento_nombre": medicamento_nombre,
        "tipo_seleccionado": filtros["tipo"],
        "fecha_desde": filtros["fecha_desde"],
        "fecha_hasta": filtros["fecha_hasta"],
        "solo_no_leidas": filtros["solo_no_leidas"],
        "buscar": filtros["buscar"],
        "total_notificaciones": stats["total"],
        "no_leidas": stats["no_leidas"],
        "total_recordatorios": stats["total_recordatorios"],
        "total_alertas": stats["total_alertas"],
        "alertas_criticas": stats["alertas_criticas"],
        "tipos": Notificacion.TIPO_CHOICES,
    }
    return render(request, "notificaciones/notifications.html", context)


@login_required
def marcar_leida_view(request: HttpRequest, notif_id: int) -> HttpResponse:
    """Marca una notificación como leída y redirige a `next` (o a notificaciones)."""
    if request.method == "POST":
        NotificacionService.marcar_como_leida(notif_id, request.user)
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("notifications")
    return redirect(next_url)


@login_required
def export_notifications_csv_view(request: HttpRequest) -> HttpResponse:
    """Exporta las notificaciones del usuario (con filtros aplicados) a CSV."""
    filtros = NotificacionService.obtener_filtros_desde_dict(request.GET.dict())
    queryset = Notificacion.objects.filter(usuario=request.user)
    queryset = NotificacionService.aplicar_filtros(queryset, filtros)
    queryset = queryset.select_related("paciente", "medicamento").order_by("-creado_en")

    csv_text = NotificacionService.exportar_csv(queryset)
    response = HttpResponse(
        "﻿" + csv_text,
        content_type="text/csv; charset=utf-8",
    )
    response["Content-Disposition"] = 'attachment; filename="notificaciones.csv"'
    return response


