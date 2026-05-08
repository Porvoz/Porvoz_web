from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.dashboard.services import DashboardService


@login_required
def dashboard_router(request: HttpRequest) -> HttpResponse:
    """Redirige al dashboard correspondiente según rol."""
    if request.user.is_staff:
        return redirect("admin_dashboard")
    return redirect("dashboard")


@login_required
def dashboard_unificado(request: HttpRequest) -> HttpResponse:
    """Dashboard con estadísticas y resumen del usuario."""
    ordenar = request.GET.get("ordenar", "recientes")
    datos = DashboardService.obtener_datos_completos(request.user, ordenar)

    context = {
        "perfil": datos["perfil"],
        "pacientes": datos["pacientes"],
        "total_medicamentos": datos["total_medicamentos"],
        "proximos_recordatorios": datos["proximos_recordatorios"],
        "actividad_reciente": datos["actividad_reciente"],
        "dias_restantes_plan": datos["dias_restantes_plan"],
        "nombre_plan": datos["nombre_plan"],
        "ordenar_actual": ordenar,
        "opciones_ordenar": datos["opciones_ordenar"],
        "llamadas_semana": datos["llamadas_semana"],
        "llamadas_atendidas_semana": datos["llamadas_atendidas_semana"],
        "llamadas_no_atendidas_semana": datos["llamadas_no_atendidas_semana"],
        "adherencia_semana": datos["adherencia_semana"],
        "pacientes_sin_medicamentos": datos["pacientes_sin_medicamentos"],
        "alertas_activas": datos["alertas_activas"],
        "proximas_llamadas": datos["proximas_llamadas"],
        "mostrar_onboarding": datos["mostrar_onboarding"],
    }

    return render(request, "dashboard/dashboard.html", context)
