"""
Tareas Celery para ejecución de llamadas.

Para correr el beat scheduler (ejecución periódica):
    celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)

# Backoff base: 30s → 60s → 120s (intento 0, 1, 2)
_RETRY_BACKOFF_BASE = 30


@shared_task(bind=True, max_retries=3, default_retry_delay=_RETRY_BACKOFF_BASE)
def ejecutar_llamada_task(self, llamada_id: int, base_url: str):
    """
    Ejecuta una llamada individual con backoff exponencial.
    Reintentos: 30s → 60s → 120s. Tras 3 fallos → DLQ (tarea marcada failed).
    """
    from apps.llamadas.models import Llamada
    from apps.llamadas.services.llamada_service import LlamadaService
    from apps.shared.middleware import get_correlation_id

    correlation_id = get_correlation_id() or "no-request"
    log_prefix = f"[LlamadaTask][{correlation_id}]"

    try:
        llamada = Llamada.objects.select_related(
            "medicamento", "paciente", "usuario"
        ).get(pk=llamada_id)
        LlamadaService._ejecutar_llamada_individual(llamada, base_url)
    except Llamada.DoesNotExist:
        logger.error(f"{log_prefix} Llamada #{llamada_id} no encontrada — descartando")
    except Exception as exc:
        countdown = _RETRY_BACKOFF_BASE * (2 ** self.request.retries)
        logger.warning(
            f"{log_prefix} Error en llamada #{llamada_id} "
            f"(intento {self.request.retries + 1}/{self.max_retries + 1}): {exc} "
            f"— reintentando en {countdown}s"
        )
        raise self.retry(exc=exc, countdown=countdown) from exc


@shared_task
def ejecutar_llamadas_pendientes_task():
    """
    Tarea periódica: busca llamadas pendientes y lanza un task por cada una.
    Configurar en django-celery-beat para ejecutar cada 60s.
    """
    from django.utils import timezone

    from apps.llamadas.models import Llamada
    from apps.llamadas.services.proveedor_voz_service import ProveedorVozService

    ahora = timezone.now()
    pendientes = list(
        Llamada.objects.filter(
            estado=Llamada.ESTADO_PROGRAMADA,
            fecha_programada__lte=ahora,
        ).values_list("id", flat=True)
    )

    if not pendientes:
        logger.info("[LlamadaTask] No hay llamadas pendientes.")
        return

    base_url = ProveedorVozService.get_base_url()
    logger.info(f"[LlamadaTask] {len(pendientes)} llamada(s) pendientes.")

    for llamada_id in pendientes:
        ejecutar_llamada_task.delay(llamada_id, base_url)
