"""
Servicios de negocio del panel de administración.
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from apps.core.models import Perfil
from apps.notificaciones.models import Notificacion
from apps.notificaciones.services.notificacion_service import NotificacionService


class CodigoService:
    """Gestión del ciclo de vida de los códigos de acceso."""

    @staticmethod
    def aplicar_codigo(usuario: User, codigo_str: str) -> tuple[bool, str]:
        """
        Canjea un código: activa el plan a partir de HOY.
        El tiempo siempre empieza en la fecha de canje, no en la de creación.
        """
        from apps.admin_panel.models import CodigoAcceso, PagoHistorico

        codigo_str = codigo_str.strip().upper()

        try:
            codigo = CodigoAcceso.objects.get(codigo=codigo_str)
        except CodigoAcceso.DoesNotExist:
            return False, "Código no encontrado. Verifica que lo hayas escrito correctamente."

        if codigo.estado != CodigoAcceso.ESTADO_DISPONIBLE:
            return False, "Este código ya fue utilizado o está cancelado."

        if codigo.fecha_limite_canje and date.today() > codigo.fecha_limite_canje:
            codigo.estado = CodigoAcceso.ESTADO_EXPIRADO
            codigo.save(update_fields=["estado"])
            return False, "Este código expiró y ya no puede canjearse."

        # Activar plan — tiempo empieza HOY
        perfil = usuario.perfil
        perfil.plan = codigo.plan
        perfil.plan_estado = Perfil.ESTADO_ACTIVO
        perfil.plan_expiration = date.today() + timedelta(days=codigo.duracion_meses * 30)
        perfil.plan_pausa_hasta = None
        perfil.plan_cancelacion_fecha = None
        perfil.save()

        # Marcar código como usado
        codigo.estado = CodigoAcceso.ESTADO_USADO
        codigo.usuario_usado_por = usuario
        codigo.usado_en = timezone.now()
        codigo.save()

        # Registrar en historial de pagos
        PagoHistorico.objects.create(
            usuario=usuario,
            plan=codigo.plan,
            duracion_meses=codigo.duracion_meses,
            tipo_pago=PagoHistorico.TIPO_CODIGO,
            codigo_usado=codigo,
            fecha_hasta=perfil.plan_expiration,
        )

        return True, f"Plan {perfil.get_plan_display()} activado hasta el {perfil.plan_expiration.strftime('%d/%m/%Y')}."

    @staticmethod
    def expirar_codigos_vencidos():
        """Marca como EXPIRADO los códigos que superaron su fecha_limite_canje."""
        from apps.admin_panel.models import CodigoAcceso
        vencidos = CodigoAcceso.objects.filter(
            estado=CodigoAcceso.ESTADO_DISPONIBLE,
            fecha_limite_canje__lt=date.today(),
        )
        count = vencidos.update(estado=CodigoAcceso.ESTADO_EXPIRADO)
        return count


class PlanExpirationService:
    """Genera notificaciones in-app cuando el plan de un usuario está por vencer."""

    DIAS_ALERTA = {
        7: (Notificacion.PRIORIDAD_NORMAL,  "Tu plan vence en 7 días"),
        3: (Notificacion.PRIORIDAD_URGENTE, "Tu plan vence en 3 días"),
        1: (Notificacion.PRIORIDAD_URGENTE, "Tu plan vence mañana"),
        0: (Notificacion.PRIORIDAD_CRITICA, "Tu plan venció hoy — renueva para seguir usando Porvoz"),
    }

    @classmethod
    def verificar_y_notificar(cls, usuario: User):
        """
        Llama desde el context processor en cada request autenticado.
        Crea como máximo una notificación de vencimiento por día.
        """
        if usuario.is_staff:
            return

        try:
            perfil = usuario.perfil
        except Exception:
            return

        if perfil.plan == Perfil.PLAN_FREEMIUM:
            return  # Gratuito no vence
        if not perfil.plan_expiration:
            return

        dias = (perfil.plan_expiration - date.today()).days

        if dias not in cls.DIAS_ALERTA:
            return

        # Solo una notificación de este tipo por día
        ya_existe = Notificacion.objects.filter(
            usuario=usuario,
            tipo=Notificacion.TIPO_SISTEMA,
            creado_en__date=date.today(),
            titulo__icontains="vence",
        ).exists()

        if ya_existe:
            return

        prioridad, titulo = cls.DIAS_ALERTA[dias]
        plan_nombre = perfil.get_plan_display()
        mensaje = (
            f"Tu plan {plan_nombre} vence el {perfil.plan_expiration.strftime('%d/%m/%Y')}. "
            "Contáctanos por WhatsApp o soporte para renovarlo fácilmente."
        )

        NotificacionService.crear_notificacion_sistema(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            prioridad=prioridad,
        )
