from django.contrib.auth.models import User
from django.db import models


class Perfil(models.Model):
    """
    Información adicional del usuario.

    Separa los datos propios de autenticación (User) de los datos de
    contacto que necesitamos en Porvoz.
    """

    ROLE_CHOICES = (
        ("caregiver", "Cuidador"),
        ("patient", "Paciente"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    phone = models.CharField("Teléfono", max_length=32)
    age = models.PositiveIntegerField("Edad")
    address = models.CharField("Dirección", max_length=255)
    role = models.CharField("Rol", max_length=20, choices=ROLE_CHOICES, default="caregiver")

    def __str__(self) -> str:
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


