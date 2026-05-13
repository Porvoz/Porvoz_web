import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def reactivar_medicamentos_pausados_task():
    """Reactiva medicamentos cuya pausa ya venció."""
    from apps.medicamentos.models import Medicamento
    n = Medicamento.objects.filter(pausado=True, pausado_hasta__lte=date.today()).update(
        pausado=False, pausado_hasta=None
    )
    logger.info("reactivar_medicamentos_pausados: reactivados=%d", n)
    return n
