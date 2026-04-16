"""
Servicio para envío de emails.
"""

import logging
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def enviar_email_bienvenida(usuario: User) -> bool:
        """Envía email de bienvenida al crear cuenta."""
        try:
            titulo = "Bienvenido a Porvoz"
            mensaje = f"""Hola {usuario.first_name or usuario.username},

¡Bienvenido a Porvoz! Ya estás listo para comenzar a registrar pacientes y medicamentos.

Próximos pasos:
1. Completa tu perfil
2. Agrega tus primeros pacientes
3. Configura los medicamentos y sus horarios
4. Los recordatorios automáticos se enviarán por teléfono

¿Preguntas? Estamos aquí para ayudarte.

Saludos,
El equipo de Porvoz"""

            send_mail(
                subject=titulo,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            logger.info(f"[Email] Bienvenida enviada a {usuario.email}")
            return True
        except Exception as e:
            logger.error(f"[Email] Error enviando bienvenida a {usuario.email}: {e}")
            return False

    @staticmethod
    def enviar_email_toma_confirmada(usuario: User, paciente_nombre: str, medicamento_nombre: str) -> bool:
        """Envía email cuando se confirma que se tomó el medicamento."""
        try:
            titulo = f"✓ {paciente_nombre} confirmó toma de {medicamento_nombre}"
            mensaje = f"""Hola,

{paciente_nombre} ha confirmado que tomó {medicamento_nombre} correctamente.

Hora: ahora
Paciente: {paciente_nombre}
Medicamento: {medicamento_nombre}

¡Excelente adherencia!

Saludos,
Porvoz"""

            send_mail(
                subject=titulo,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            logger.info(f"[Email] Toma confirmada enviado a {usuario.email}")
            return True
        except Exception as e:
            logger.error(f"[Email] Error enviando confirmación a {usuario.email}: {e}")
            return False

    @staticmethod
    def enviar_email_toma_no_confirmada(usuario: User, paciente_nombre: str, medicamento_nombre: str) -> bool:
        """Envía email cuando no se confirma la toma del medicamento."""
        try:
            titulo = f"✗ {paciente_nombre} no tomó {medicamento_nombre}"
            mensaje = f"""Hola,

{paciente_nombre} reportó que NO tomó {medicamento_nombre}.

Paciente: {paciente_nombre}
Medicamento: {medicamento_nombre}

Requiere tu atención. Por favor contacta al paciente.

Saludos,
Porvoz"""

            send_mail(
                subject=titulo,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            logger.info(f"[Email] Toma no confirmada enviado a {usuario.email}")
            return True
        except Exception as e:
            logger.error(f"[Email] Error enviando no confirmación a {usuario.email}: {e}")
            return False

    @staticmethod
    def enviar_email_toma_aplazada(usuario: User, paciente_nombre: str, medicamento_nombre: str) -> bool:
        """Envía email cuando el paciente aplaza la toma del medicamento."""
        try:
            titulo = f"⏰ {paciente_nombre} aplazó toma de {medicamento_nombre}"
            mensaje = f"""Hola,

{paciente_nombre} indicó que tomará {medicamento_nombre} más tarde.

Paciente: {paciente_nombre}
Medicamento: {medicamento_nombre}

Se configuró un reintento automático. Te notificaremos si hay cambios.

Saludos,
Porvoz"""

            send_mail(
                subject=titulo,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            logger.info(f"[Email] Toma aplazada enviado a {usuario.email}")
            return True
        except Exception as e:
            logger.error(f"[Email] Error enviando aplazamiento a {usuario.email}: {e}")
            return False

    @staticmethod
    def enviar_email_llamada_no_atendida(usuario: User, paciente_nombre: str, medicamento_nombre: str) -> bool:
        """Envía email cuando la llamada no fue atendida."""
        try:
            titulo = f"⚠ {paciente_nombre} no atendió la llamada de {medicamento_nombre}"
            mensaje = f"""Hola,

{paciente_nombre} no respondió la llamada de recordatorio.

Paciente: {paciente_nombre}
Medicamento: {medicamento_nombre}

Intenta contactar al paciente manualmente.

Saludos,
Porvoz"""

            send_mail(
                subject=titulo,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            logger.info(f"[Email] Llamada no atendida enviado a {usuario.email}")
            return True
        except Exception as e:
            logger.error(f"[Email] Error enviando llamada no atendida a {usuario.email}: {e}")
            return False
