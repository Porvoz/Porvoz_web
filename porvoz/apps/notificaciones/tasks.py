"""
Tareas Celery para envío de emails.

Si Celery no está corriendo, .delay() falla silenciosamente y el email no se envía.
Para correr el worker:
    celery -A config worker --loglevel=info
"""

import logging

from celery import shared_task
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email_task(self, tipo: str, usuario_id: int, paciente_id=None, medicamento_id=None, extra: dict = None):
    """
    Tarea Celery para enviar emails de notificación de forma asíncrona.

    Args:
        tipo: 'toma_confirmada' | 'toma_no_confirmada' | 'toma_aplazada' |
              'llamada_no_atendida' | 'reintentos_agotados' |
              'emergencia_medica' | 'rechazo_tratamiento'
        usuario_id: ID del User destinatario
        paciente_id: ID del Paciente (opcional)
        medicamento_id: ID del Medicamento (opcional)
        extra: kwargs adicionales pasados al handler (ej: {'intentos': 3})
    """
    from apps.medicamentos.models import Medicamento
    from apps.notificaciones.services.email_service import EmailService
    from apps.pacientes.models import Paciente

    extra = extra or {}

    try:
        usuario = User.objects.get(id=usuario_id)
        paciente = Paciente.objects.filter(id=paciente_id).first() if paciente_id else None
        medicamento = Medicamento.objects.filter(id=medicamento_id).first() if medicamento_id else None

        # Eventos críticos para seguridad del paciente — el email NO se filtra
        # por preferencias y va al método obligatorio.
        if tipo in ("emergencia_medica", "rechazo_tratamiento"):
            titulo = extra.get("titulo") or "Alerta crítica de Porvoz"
            mensaje = extra.get("mensaje") or ""
            enviado = EmailService.enviar_email_critico_obligatorio(
                usuario=usuario,
                titulo=titulo,
                mensaje=mensaje,
                paciente=paciente,
                medicamento=medicamento,
            )
            if enviado:
                logger.info(f"[EmailTask] CRÍTICO {tipo} → usuario {usuario_id}")
            return

        handlers = {
            "toma_confirmada":    EmailService.enviar_email_toma_confirmada,
            "toma_no_confirmada": EmailService.enviar_email_toma_no_confirmada,
            "toma_aplazada":      EmailService.enviar_email_toma_aplazada,
            "llamada_no_atendida":EmailService.enviar_email_llamada_no_atendida,
            "reintentos_agotados":EmailService.enviar_email_reintentos_agotados,
        }

        handler = handlers.get(tipo)
        if not handler:
            logger.error(f"[EmailTask] Tipo desconocido: {tipo}")
            return

        enviado = handler(usuario=usuario, paciente=paciente, medicamento=medicamento, **extra)
        if enviado:
            logger.info(f"[EmailTask] OK — {tipo} → usuario {usuario_id}")
        else:
            logger.info(f"[EmailTask] No enviado (preferencia desactivada) — {tipo} → usuario {usuario_id}")

    except User.DoesNotExist:
        logger.error(f"[EmailTask] Usuario {usuario_id} no encontrado")
    except Exception as exc:
        logger.error(f"[EmailTask] Error en {tipo}: {exc}", exc_info=True)
        raise self.retry(exc=exc) from exc
