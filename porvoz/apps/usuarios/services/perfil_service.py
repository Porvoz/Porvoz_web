"""
Servicio para gestionar perfiles de usuario.
"""

from datetime import date, datetime, timedelta

from apps.core.models import Perfil
from apps.shared.services import TelefonoService


class PerfilService:
    """Encapsula la lógica de gestión de perfiles."""

    @staticmethod
    def validar_edad(
        date_of_birth_str: str,
    ) -> tuple[date | None, str | None]:
        """
        Valida que la fecha de nacimiento sea válida y represente una edad >= 10 años.

        Args:
            date_of_birth_str: Fecha en formato "YYYY-MM-DD"

        Returns:
            Tuple[date | None, str | None] — (fecha_parseada, mensaje_error)
            Si es válido: (fecha, None)
            Si es inválido: (None, mensaje_error)
        """
        if not date_of_birth_str:
            return None, None

        try:
            birth_date = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
        except ValueError:
            return None, "Fecha de nacimiento inválida."

        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

        if age < 10:
            return None, "Debes tener al menos 10 años para registrarte."

        return birth_date, None

    @staticmethod
    def actualizar_perfil(
        perfil: Perfil,
        first_name: str = "",
        last_name: str = "",
        city: str = "",
        phone_country: str = "+57",
        phone_number: str = "",
        document_type: str = "",
        document_number: str = "",
        date_of_birth_str: str = "",
        emergency_contact_name: str = "",
        emergency_contact_phone_country: str = "+57",
        emergency_contact_phone_number: str = "",
        profile_image=None,
        email_toma_confirmada: bool = None,
        email_toma_no_confirmada: bool = None,
        email_llamada_no_atendida: bool = None,
        email_toma_aplazada: bool = None,
        email_reintentos_agotados: bool = None,
    ) -> tuple[bool, str | None]:
        """
        Actualiza los datos del perfil y del usuario asociado.

        Args:
            perfil: Objeto Perfil a actualizar
            first_name: Nombre
            last_name: Apellido
            city: Ciudad
            phone_country: Código país teléfono
            phone_number: Número teléfono
            document_type: Tipo de documento
            document_number: Número de documento
            date_of_birth_str: Fecha de nacimiento en formato "YYYY-MM-DD"
            emergency_contact_name: Nombre contacto emergencia
            emergency_contact_phone_country: Código país contacto
            emergency_contact_phone_number: Número contacto
            profile_image: Archivo de imagen (opcional)
            email_toma_confirmada: Recibir email cuando medicamento es confirmado
            email_toma_no_confirmada: Recibir email cuando medicamento NO es confirmado
            email_llamada_no_atendida: Recibir email cuando llamada no es atendida
            email_toma_aplazada: Recibir email cuando se aplaza medicamento
            email_reintentos_agotados: Recibir email cuando se agotan reintentos

        Returns:
            Tuple[bool, Optional[str]] — (éxito, mensaje_error)
        """
        # Validar edad si se proporciona
        if date_of_birth_str:
            birth_date, error_msg = PerfilService.validar_edad(date_of_birth_str)
            if error_msg:
                return False, error_msg
            perfil.date_of_birth = birth_date
        else:
            perfil.date_of_birth = None

        # Actualizar campos de perfil
        perfil.first_name = first_name
        perfil.last_name = last_name
        perfil.city = city
        perfil.phone = TelefonoService.formatear_completo(phone_country, phone_number)
        perfil.document_type = document_type
        perfil.document_number = document_number
        perfil.emergency_contact_name = emergency_contact_name
        perfil.emergency_contact_phone = TelefonoService.formatear_completo(
            emergency_contact_phone_country, emergency_contact_phone_number
        )

        # Actualizar preferencias de email
        if email_toma_confirmada is not None:
            perfil.email_toma_confirmada = email_toma_confirmada
        if email_toma_no_confirmada is not None:
            perfil.email_toma_no_confirmada = email_toma_no_confirmada
        if email_llamada_no_atendida is not None:
            perfil.email_llamada_no_atendida = email_llamada_no_atendida
        if email_toma_aplazada is not None:
            perfil.email_toma_aplazada = email_toma_aplazada
        if email_reintentos_agotados is not None:
            perfil.email_reintentos_agotados = email_reintentos_agotados

        if profile_image:
            perfil.profile_image = profile_image

        perfil.profile_completed = True
        perfil.save()

        # Sincronizar nombre en el usuario Django
        if perfil.user:
            perfil.user.first_name = first_name or perfil.user.first_name
            perfil.user.last_name = last_name or perfil.user.last_name
            perfil.user.save()

        return True, None

    @staticmethod
    def get_dias_restantes_plan(perfil: Perfil) -> int:
        """Días restantes del plan. Si no hay fecha de vencimiento, retorna 365."""
        if perfil.plan_expiration:
            from django.utils import timezone
            delta = (perfil.plan_expiration - timezone.now().date()).days
            return max(0, delta)
        return 365

    @staticmethod
    def cambiar_plan(perfil: Perfil, nuevo_plan: str) -> tuple[bool, str | None]:
        """
        Cambia el plan del perfil a uno válido.

        Args:
            perfil: Objeto Perfil a actualizar
            nuevo_plan: Uno de: "freemium", "growth", "multi_business"

        Returns:
            Tuple[bool, Optional[str]] — (éxito, mensaje_error)
        """
        planes_validos = [
            Perfil.PLAN_FREEMIUM,
            Perfil.PLAN_GROWTH,
            Perfil.PLAN_MULTI_BUSINESS,
        ]

        if nuevo_plan not in planes_validos:
            return False, f"Plan inválido. Opciones: {', '.join(planes_validos)}"

        perfil.plan = nuevo_plan
        perfil.plan_expiration = date.today() + timedelta(days=365)
        perfil.save()

        return True, None
