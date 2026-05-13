import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def verificar_estados_plan_task():
    """
    Tarea diaria que:
    - Reactiva planes cuya pausa venció.
    - Baja a Básico planes cuya cancelación llegó a fecha.
    """
    from apps.core.models import Perfil

    hoy = date.today()

    reactivados = Perfil.objects.filter(
        plan_estado=Perfil.ESTADO_PAUSADO,
        plan_pausa_hasta__lte=hoy,
    ).update(plan_estado=Perfil.ESTADO_ACTIVO, plan_pausa_hasta=None)

    cancelados = Perfil.objects.filter(
        plan_estado=Perfil.ESTADO_CANCELADO,
        plan_cancelacion_fecha__lte=hoy,
    )
    n_cancelados = cancelados.count()
    cancelados.update(
        plan=Perfil.PLAN_FREEMIUM,
        plan_estado=Perfil.ESTADO_ACTIVO,
        plan_cancelacion_fecha=None,
        plan_expiration=None,
    )

    logger.info("verificar_estados_plan: reactivados=%d bajados_a_basico=%d", reactivados, n_cancelados)
    return {"reactivados": reactivados, "bajados_a_basico": n_cancelados}
