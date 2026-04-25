"""
Servicio para envío de emails con plantillas HTML.
"""

import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.urls import reverse
from apps.notificaciones.models import Notificacion

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def _get_base_url() -> str:
        """Obtiene la URL base de la aplicación."""
        protocol = "https" if not settings.DEBUG else "http"
        domain = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "localhost:8000"
        return f"{protocol}://{domain}"

    @staticmethod
    def _debe_enviar_email(usuario: User, tipo_email: str, prioridad: str = None) -> bool:
        """
        Verifica si el usuario desea recibir este tipo de email.

        Lógica:
        - email_urgente_minimo=True (default): enviar SOLO prioridades CRITICA/URGENTE,
          ignorando todas las demás preferencias. Si prioridad es None o baja → no enviar.
        - email_urgente_minimo=False: respetar cada preferencia específica.
        """
        try:
            perfil = usuario.perfil
        except Exception:
            logger.warning(f"[Email] Usuario {usuario.username} no tiene perfil — no se envía email")
            return False

        if perfil.email_urgente_minimo:
            # Modo restrictivo: solo CRITICA/URGENTE pasan, sin excepción
            result = prioridad in [Notificacion.PRIORIDAD_CRITICA, Notificacion.PRIORIDAD_URGENTE]
            if not result:
                logger.info(
                    f"[Email] Bloqueado por email_urgente_minimo: tipo={tipo_email} prioridad={prioridad}"
                )
            return result

        # Modo normal: cada tipo tiene su preferencia
        preferencias = {
            "toma_confirmada":      perfil.email_toma_confirmada,
            "toma_no_confirmada":   perfil.email_toma_no_confirmada,
            "llamada_no_atendida":  perfil.email_llamada_no_atendida,
            "toma_aplazada":        perfil.email_toma_aplazada,
            "reintentos_agotados":  perfil.email_reintentos_agotados,
        }
        result = preferencias.get(tipo_email, False)
        if not result:
            logger.info(f"[Email] Preferencia desactivada: tipo={tipo_email}")
        return result

    @staticmethod
    def enviar_notificacion_html(
        usuario: User,
        titulo: str,
        tipo_notificacion: str,
        mensaje: str = "",
        paciente=None,
        medicamento=None,
        prioridad: str = None,
        url_detalle: str = None,
    ) -> bool:
        """
        Envía email HTML de notificación comprobando preferencias del usuario.

        Args:
            usuario: Usuario destinatario
            titulo: Título del email
            tipo_notificacion: Tipo de notificación ('toma_confirmada', 'toma_no_confirmada', etc.)
            mensaje: Mensaje principal
            paciente: Objeto paciente (opcional)
            medicamento: Objeto medicamento (opcional)
            prioridad: Nivel de prioridad
            url_detalle: URL para enlace de detalles
        """
        if not usuario.email:
            logger.warning(f"[Email] Usuario {usuario.username} no tiene email configurado")
            return False

        # Verificar preferencias
        if not EmailService._debe_enviar_email(usuario, tipo_notificacion, prioridad):
            logger.info(f"[Email] {usuario.email} rechazó email de tipo {tipo_notificacion}")
            return False

        try:
            # Seleccionar plantilla según tipo
            plantilla_map = {
                "toma_confirmada":    "notificaciones/emails/notificacion_toma_confirmada.html",
                "toma_no_confirmada": "notificaciones/emails/notificacion_toma_no_confirmada.html",
                "toma_aplazada":      "notificaciones/emails/notificacion_toma_aplazada.html",
                "llamada_no_atendida":"notificaciones/emails/notificacion_llamada_no_atendida.html",
                "reintentos_agotados":"notificaciones/emails/notificacion_llamada_no_atendida.html",
                "alerta":             "notificaciones/emails/notificacion_alerta.html",
            }

            plantilla = plantilla_map.get(tipo_notificacion, "notificaciones/emails/notificacion_alerta.html")

            # Contexto para la plantilla
            base_url = EmailService._get_base_url()
            contexto = {
                "titulo": titulo,
                "mensaje": mensaje,
                "paciente": paciente,
                "medicamento": medicamento,
                "prioridad": prioridad,
                "url_detalle": url_detalle or "",
                "url_app": f"{base_url}/dashboard/",
                "url_preferencias": f"{base_url}/usuarios/editar-perfil/",
            }

            # Renderizar plantilla HTML
            html_content = render_to_string(plantilla, contexto)

            # Crear email con alternativa HTML
            email = EmailMultiAlternatives(
                subject=titulo,
                body=f"Para ver este mensaje, abre tu cliente de email con soporte HTML.\n\n{mensaje}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[usuario.email],
            )

            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            logger.info(f"[Email] {tipo_notificacion} enviado a {usuario.email}")
            return True

        except Exception as e:
            logger.error(f"[Email] Error enviando {tipo_notificacion} a {usuario.email}: {e}")
            return False

    @staticmethod
    def enviar_email_bienvenida(usuario: User) -> bool:
        """Envía email de bienvenida al crear cuenta."""
        try:
            titulo = "¡Bienvenido a Porvoz!"
            contexto = {
                "titulo": titulo,
                "mensaje": f"""Hola {usuario.first_name or usuario.username},

¡Bienvenido a Porvoz! Ya estás listo para comenzar a registrar pacientes y medicamentos.

Próximos pasos:
1. Completa tu perfil
2. Agrega tus primeros pacientes
3. Configura los medicamentos y sus horarios
4. Los recordatorios automáticos se enviarán por teléfono

¿Preguntas? Estamos aquí para ayudarte.""",
                "url_app": f"{EmailService._get_base_url()}/dashboard/",
                "url_preferencias": f"{EmailService._get_base_url()}/usuarios/editar-perfil/",
            }

            html_content = render_to_string("notificaciones/emails/base_email.html", contexto)
            email = EmailMultiAlternatives(
                subject=titulo,
                body="Abre tu cliente de email con soporte HTML para ver este mensaje.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[usuario.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            logger.info(f"[Email] Bienvenida enviada a {usuario.email}")
            return True
        except Exception as e:
            logger.error(f"[Email] Error enviando bienvenida a {usuario.email}: {e}")
            return False

    @staticmethod
    def enviar_email_toma_confirmada(usuario: User, paciente=None, medicamento=None, url_detalle: str = None) -> bool:
        """Envía email cuando se confirma que se tomó el medicamento."""
        titulo = "✓ Medicamento Confirmado"
        mensaje = f"{paciente.nombre if paciente else 'El paciente'} confirmó la toma de {medicamento.nombre if medicamento else 'un medicamento'}"

        return EmailService.enviar_notificacion_html(
            usuario=usuario,
            titulo=titulo,
            tipo_notificacion="toma_confirmada",
            mensaje=mensaje,
            paciente=paciente,
            medicamento=medicamento,
            prioridad=Notificacion.PRIORIDAD_BAJA,
            url_detalle=url_detalle,
        )

    @staticmethod
    def enviar_email_toma_no_confirmada(usuario: User, paciente=None, medicamento=None, url_detalle: str = None) -> bool:
        """Envía email cuando no se confirma la toma del medicamento."""
        titulo = "⚠️ Medicamento No Confirmado"
        mensaje = f"{paciente.nombre if paciente else 'El paciente'} NO confirmó la toma de {medicamento.nombre if medicamento else 'un medicamento'}"

        return EmailService.enviar_notificacion_html(
            usuario=usuario,
            titulo=titulo,
            tipo_notificacion="toma_no_confirmada",
            mensaje=mensaje,
            paciente=paciente,
            medicamento=medicamento,
            prioridad=Notificacion.PRIORIDAD_URGENTE,
            url_detalle=url_detalle,
        )

    @staticmethod
    def enviar_email_toma_aplazada(usuario: User, paciente=None, medicamento=None, url_detalle: str = None) -> bool:
        """Envía email cuando el paciente aplaza la toma del medicamento."""
        titulo = "⏱️ Medicamento Aplazado"
        mensaje = f"{paciente.nombre if paciente else 'El paciente'} aplazó la toma de {medicamento.nombre if medicamento else 'un medicamento'}"

        return EmailService.enviar_notificacion_html(
            usuario=usuario,
            titulo=titulo,
            tipo_notificacion="toma_aplazada",
            mensaje=mensaje,
            paciente=paciente,
            medicamento=medicamento,
            prioridad=Notificacion.PRIORIDAD_NORMAL,
            url_detalle=url_detalle,
        )

    @staticmethod
    def enviar_email_llamada_no_atendida(usuario: User, paciente=None, medicamento=None, url_detalle: str = None) -> bool:
        """Envía email cuando la llamada no fue atendida."""
        titulo = "📞 Llamada No Atendida"
        mensaje = f"La llamada de recordatorio para {medicamento.nombre if medicamento else 'un medicamento'} de {paciente.nombre if paciente else 'un paciente'} no fue atendida"

        return EmailService.enviar_notificacion_html(
            usuario=usuario,
            titulo=titulo,
            tipo_notificacion="llamada_no_atendida",
            mensaje=mensaje,
            paciente=paciente,
            medicamento=medicamento,
            prioridad=Notificacion.PRIORIDAD_URGENTE,
            url_detalle=url_detalle,
        )

    @staticmethod
    def enviar_email_reintentos_agotados(usuario: User, paciente=None, medicamento=None, intentos: int = 0, url_detalle: str = None) -> bool:
        """Envía email cuando se agotan todos los reintentos sin respuesta del paciente."""
        nombre_med = medicamento.nombre if medicamento else "un medicamento"
        nombre_pac = paciente.nombre if paciente else "un paciente"
        titulo = f"Sin respuesta tras {intentos} intento(s) — {nombre_med}"
        mensaje = (
            f"{nombre_pac} no respondió la llamada de recordatorio para {nombre_med} "
            f"después de {intentos} intento(s) automático(s). Se requiere atención manual."
        )
        return EmailService.enviar_notificacion_html(
            usuario=usuario,
            titulo=titulo,
            tipo_notificacion="reintentos_agotados",
            mensaje=mensaje,
            paciente=paciente,
            medicamento=medicamento,
            prioridad=Notificacion.PRIORIDAD_CRITICA,
            url_detalle=url_detalle,
        )

    @staticmethod
    def enviar_email_alerta(usuario: User, titulo: str, mensaje: str, paciente=None, medicamento=None, prioridad: str = None, url_detalle: str = None) -> bool:
        """Envía email de alerta personalizado."""
        return EmailService.enviar_notificacion_html(
            usuario=usuario,
            titulo=titulo,
            tipo_notificacion="alerta",
            mensaje=mensaje,
            paciente=paciente,
            medicamento=medicamento,
            prioridad=prioridad or Notificacion.PRIORIDAD_URGENTE,
            url_detalle=url_detalle,
        )

    @staticmethod
    def enviar_email_critico_obligatorio(
        usuario: User,
        titulo: str,
        mensaje: str,
        paciente=None,
        medicamento=None,
        url_detalle: str = None,
    ) -> bool:
        """
        Envía un email crítico saltándose las preferencias del usuario.
        Reservado para escenarios de seguridad del paciente (síntomas graves
        durante una llamada, rechazo explícito de tratamiento). Estos eventos
        nunca pueden silenciarse por configuración.
        """
        if not usuario.email:
            logger.warning(f"[Email] Crítico: usuario {usuario.username} sin email")
            return False
        try:
            base_url = EmailService._get_base_url()
            contexto = {
                "titulo": titulo,
                "mensaje": mensaje,
                "paciente": paciente,
                "medicamento": medicamento,
                "prioridad": Notificacion.PRIORIDAD_CRITICA,
                "url_detalle": url_detalle or "",
                "url_app": f"{base_url}/dashboard/",
                "url_preferencias": f"{base_url}/usuarios/editar-perfil/",
            }
            html_content = render_to_string(
                "notificaciones/emails/notificacion_alerta.html", contexto
            )
            email = EmailMultiAlternatives(
                subject=titulo,
                body=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[usuario.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            logger.info(f"[Email] CRÍTICO obligatorio enviado a {usuario.email}: {titulo}")
            return True
        except Exception as e:
            logger.error(f"[Email] Error en crítico obligatorio a {usuario.email}: {e}")
            return False
