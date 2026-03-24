"""
Servicio para crear cuentas de usuario con perfil.
"""

from datetime import date, timedelta
from typing import Optional, Tuple

from django.contrib.auth.models import User

from apps.core.models import Perfil
from apps.shared.services import TelefonoService


class RegistroService:
    """Encapsula la lógica de creación de usuario y perfil."""

    @staticmethod
    def crear_usuario_y_perfil(
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone_country: str = "+57",
        phone_number: str = "",
        document_type: str = "",
        document_number: str = "",
        date_of_birth: Optional[date] = None,
        city: str = "",
        emergency_contact_name: str = "",
        emergency_contact_phone_country: str = "+57",
        emergency_contact_phone_number: str = "",
    ) -> Tuple[User, Perfil]:
        """
        Crea un usuario y su perfil asociado.

        Args:
            username: Nombre de usuario único
            email: Email único
            password: Contraseña
            first_name: Nombre
            last_name: Apellido
            phone_country: Código país del teléfono (ej: +57)
            phone_number: Número de teléfono
            document_type: Tipo de documento (cc, ce, ti, pp)
            document_number: Número de documento
            date_of_birth: Fecha de nacimiento
            city: Ciudad
            emergency_contact_name: Nombre contacto emergencia
            emergency_contact_phone_country: Código país contacto
            emergency_contact_phone_number: Número contacto

        Returns:
            Tuple[User, Perfil] — El usuario y perfil creados

        Raises:
            ValueError si algún parámetro es inválido
        """
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Formatear teléfonos
        phone = TelefonoService.formatear_completo(phone_country, phone_number)
        emergency_phone = TelefonoService.formatear_completo(
            emergency_contact_phone_country, emergency_contact_phone_number
        )

        # Calcular expiración de plan (365 días desde hoy)
        plan_expiration = date.today() + timedelta(days=365)

        # Crear perfil
        perfil = Perfil.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            document_type=document_type or "",
            document_number=document_number,
            date_of_birth=date_of_birth,
            city=city,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone=emergency_phone,
            profile_completed=True,
            plan_expiration=plan_expiration,
        )

        return user, perfil
