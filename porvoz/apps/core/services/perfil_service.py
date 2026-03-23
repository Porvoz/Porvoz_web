"""
Servicio para gestionar perfiles de usuario.
"""
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

from django.contrib.auth.models import User

from apps.core.models import Perfil
from .telefono_service import TelefonoService


class PerfilService:
    """Encapsula la lógica de gestión de perfiles."""

    @staticmethod
    def validar_edad(
        date_of_birth_str: str,
    ) -> Tuple[Optional[date], Optional[str]]:
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
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
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
    ) -> Tuple[bool, Optional[str]]:
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
    def cambiar_plan(
        perfil: Perfil, nuevo_plan: str
    ) -> Tuple[bool, Optional[str]]:
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
