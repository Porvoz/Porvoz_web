"""
Context processors para que el sidebar y otras plantillas tengan siempre
el mismo contexto (p. ej. perfil) en todas las vistas.
"""

from .models import Perfil


def perfil_sidebar(request):
    """
    Añade perfil, conteos de notificaciones y dispara alertas de vencimiento de plan.
    """
    if request.user.is_authenticated:
        perfil, _ = Perfil.objects.get_or_create(user=request.user)
        from apps.notificaciones.models import Notificacion

        # Verificar vencimiento de plan (máx. una notif/día, sin bloquear el request)
        try:
            from apps.admin_panel.services import PlanExpirationService
            PlanExpirationService.verificar_y_notificar(request.user)
        except Exception:
            pass

        base_qs = Notificacion.objects.filter(usuario=request.user, leida=False)
        no_leidas = base_qs.count()
        alertas_no_leidas = base_qs.filter(tipo=Notificacion.TIPO_ALERTA).count()

        # Días restantes del plan para el banner de la UI
        dias_plan = None
        if not request.user.is_staff and perfil.plan != Perfil.PLAN_FREEMIUM and perfil.plan_expiration:
            from datetime import date
            dias_plan = (perfil.plan_expiration - date.today()).days

        return {
            "perfil": perfil,
            "no_leidas_notificaciones": no_leidas,
            "alertas_no_leidas": alertas_no_leidas,
            "dias_plan_restantes": dias_plan,
        }
    return {
        "perfil": None,
        "no_leidas_notificaciones": 0,
        "alertas_no_leidas": 0,
        "dias_plan_restantes": None,
    }
