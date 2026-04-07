"""
Sistema de auditoría para registrar cambios en modelos
"""

import logging
from django.contrib.auth.models import User
from apps.llamadas.models import AuditoriaLog

logger = logging.getLogger(__name__)

    @staticmethod
    def registrar(
        usuario: User,
        obj,
        accion: str,
        cambios: dict = None,
        request=None,
    ):
        """
        Registra un cambio en la auditoría.

        Args:
            usuario: Usuario que realizó el cambio
            obj: Instancia del modelo afectado
            accion: 'create', 'update' o 'delete'
            cambios: Dict con cambios (para UPDATE)
            request: HttpRequest para obtener IP y User Agent
        """
        try:
            content_type = ContentType.objects.get_for_model(obj.__class__)
            ip_address = None
            user_agent = ""

            if request:
                ip_address = AuditoriaLog._get_client_ip(request)
                user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

            AuditoriaLog.objects.create(
                usuario=usuario,
                contenido_type=content_type,
                objeto_id=obj.pk,
                objeto_str=str(obj),
                accion=accion,
                cambios=cambios or {},
                ip_address=ip_address,
                user_agent=user_agent,
            )

            logger.info(
                f"[Audit] {usuario} {accion} {content_type} #{obj.pk}"
            )

        except Exception as e:
            logger.error(f"[Audit] Error registrando auditoría: {e}")

    @staticmethod
    def _get_client_ip(request):
        """Obtiene IP del cliente desde request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
