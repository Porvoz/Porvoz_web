from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """
    Perfil extendido para usuarios de Porvoz.
    """

    ROLE_PATIENT = "patient"
    ROLE_CAREGIVER = "caregiver"
    ROLE_CHOICES = [
        (ROLE_CAREGIVER, "Cuidador"),
        (ROLE_PATIENT, "Paciente"),
    ]
    DOC_CC = "cc"
    DOC_CE = "ce"
    DOC_TI = "ti"
    DOC_PP = "pp"
    DOC_CHOICES = [
        (DOC_CC, "Cédula de ciudadanía"),
        (DOC_CE, "Cédula de extranjería"),
        (DOC_TI, "Tarjeta de identidad"),
        (DOC_PP, "Pasaporte"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    role = models.CharField("Rol", max_length=20, choices=ROLE_CHOICES)
    first_name = models.CharField("Nombre", max_length=150, blank=True)
    last_name = models.CharField("Apellidos", max_length=150, blank=True)
    date_of_birth = models.DateField("Fecha de nacimiento", blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True)
    phone = models.CharField("Teléfono", max_length=30, blank=True)
    profile_image = models.ImageField("Foto de perfil", upload_to="profile_images/", blank=True, null=True)
    document_type = models.CharField("Tipo de documento", max_length=10, choices=DOC_CHOICES, blank=True)
    document_number = models.CharField("Número de documento", max_length=30, blank=True)
    emergency_contact_name = models.CharField("Nombre contacto de emergencia", max_length=150, blank=True)
    emergency_contact_phone = models.CharField("Teléfono contacto de emergencia", max_length=30, blank=True)
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
        db_table = "porvoz_perfil"

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_role_display()})"

