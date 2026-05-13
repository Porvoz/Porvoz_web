"""Tarea Celery para el resumen semanal de adherencia."""
import logging
from datetime import date, timedelta

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def enviar_resumen_semanal_task():
    """
    Cada lunes envía a cada cuidador activo un resumen de la semana anterior:
    pacientes, llamadas confirmadas/no atendidas y adherencia %.
    """
    from django.contrib.auth.models import User
    from django.core.mail import send_mail
    from django.template.loader import render_to_string

    from apps.llamadas.models import Llamada
    from apps.pacientes.models import Paciente

    hoy = date.today()
    inicio = hoy - timedelta(days=7)

    usuarios = User.objects.filter(is_active=True).select_related("perfil")
    enviados = 0

    for usuario in usuarios:
        try:
            perfil = getattr(usuario, "perfil", None)
            if not perfil or not usuario.email:
                continue

            pacientes = Paciente.objects.filter(usuario=usuario, activo=True)
            if not pacientes.exists():
                continue

            llamadas_semana = Llamada.objects.filter(
                usuario=usuario,
                fecha_programada__date__gte=inicio,
                fecha_programada__date__lt=hoy,
            )
            total = llamadas_semana.count()
            confirmadas = llamadas_semana.filter(respuesta__resultado="confirmada").count()
            no_atendidas = llamadas_semana.filter(respuesta__resultado="sin_confirmar").count()
            adherencia = round(confirmadas * 100 / total) if total else 0

            context = {
                "usuario": usuario,
                "pacientes": pacientes,
                "total_llamadas": total,
                "confirmadas": confirmadas,
                "no_atendidas": no_atendidas,
                "adherencia": adherencia,
                "inicio": inicio,
                "fin": hoy - timedelta(days=1),
            }

            cuerpo = render_to_string("emails/resumen_semanal.html", context)
            send_mail(
                subject=f"Resumen semanal Porvoz — {inicio.strftime('%d/%m')} al {(hoy - timedelta(days=1)).strftime('%d/%m/%Y')}",
                message="",
                html_message=cuerpo,
                from_email=None,
                recipient_list=[usuario.email],
                fail_silently=True,
            )
            enviados += 1
        except Exception as e:
            logger.error("resumen_semanal error usuario=%s: %s", usuario.id, e)

    logger.info("resumen_semanal_task: enviados=%d", enviados)
    return enviados
