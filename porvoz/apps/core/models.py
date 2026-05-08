from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """
    Perfil extendido para usuarios de Porvoz.
    """

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
    first_name = models.CharField("Nombre", max_length=150, blank=True)
    last_name = models.CharField("Apellidos", max_length=150, blank=True)
    date_of_birth = models.DateField("Fecha de nacimiento", blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True)
    phone = models.CharField("Teléfono", max_length=30, blank=True)
    profile_image = models.ImageField(
        "Foto de perfil", upload_to="profile_images/", blank=True, null=True
    )
    document_type = models.CharField(
        "Tipo de documento", max_length=10, choices=DOC_CHOICES, blank=True
    )
    document_number = models.CharField("Número de documento", max_length=30, blank=True)
    emergency_contact_name = models.CharField(
        "Nombre contacto de emergencia", max_length=150, blank=True
    )
    emergency_contact_phone = models.CharField(
        "Teléfono contacto de emergencia", max_length=30, blank=True
    )
    profile_completed = models.BooleanField(default=False)

    # Planes
    PLAN_FREEMIUM = "freemium"          # Gratuito — clave legacy, no rompe datos existentes
    PLAN_GROWTH = "growth"              # Básico
    PLAN_MULTI_BUSINESS = "multi_business"  # Familiar
    PLAN_PROFESIONAL = "profesional"    # Profesional
    PLAN_CHOICES = [
        (PLAN_FREEMIUM, "Gratuito"),
        (PLAN_GROWTH, "Básico"),
        (PLAN_MULTI_BUSINESS, "Familiar"),
        (PLAN_PROFESIONAL, "Profesional"),
    ]
    plan = models.CharField(
        "Plan",
        max_length=20,
        choices=PLAN_CHOICES,
        default=PLAN_FREEMIUM,
        help_text="Plan de suscripción del usuario",
    )
    plan_expiration = models.DateField(
        "Vencimiento del plan",
        null=True,
        blank=True,
        help_text="Fecha hasta la cual el plan está activo",
    )

    ESTADO_ACTIVO = "activo"
    ESTADO_PAUSADO = "pausado"
    ESTADO_CANCELADO = "cancelado"
    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_PAUSADO, "Pausado"),
        (ESTADO_CANCELADO, "Cancelado"),
    ]
    plan_estado = models.CharField(
        "Estado del plan",
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
    )
    plan_pausa_hasta = models.DateField(
        "Plan pausado hasta",
        null=True,
        blank=True,
        help_text="Fecha hasta la cual el plan permanece pausado (se reactiva automáticamente)",
    )
    plan_cancelacion_fecha = models.DateField(
        "Fecha de baja por cancelación",
        null=True,
        blank=True,
        help_text="El plan sigue activo hasta esta fecha, luego baja a Básico",
    )

    # Preferencias de notificación por email
    email_toma_confirmada = models.BooleanField(
        "Notificar cuando medicamento es tomado",
        default=True,
        help_text="Recibir email cuando se confirma que un medicamento fue tomado",
    )
    email_toma_no_confirmada = models.BooleanField(
        "Notificar cuando medicamento NO es tomado",
        default=True,
        help_text="Recibir email cuando se registra que un medicamento no fue tomado",
    )
    email_llamada_no_atendida = models.BooleanField(
        "Notificar llamadas no atendidas",
        default=True,
        help_text="Recibir email cuando una llamada de recordatorio no es atendida",
    )
    email_toma_aplazada = models.BooleanField(
        "Notificar cuando paciente aplaza medicamento",
        default=True,
        help_text="Recibir email cuando un paciente indica que tomará el medicamento después",
    )
    email_reintentos_agotados = models.BooleanField(
        "Notificar cuando se agotan todos los reintentos",
        default=True,
        help_text="Recibir email cuando el paciente no responde tras todos los intentos automáticos",
    )
    # Mantenido por compatibilidad con registros existentes; ya no se usa en la UI
    email_urgente_minimo = models.BooleanField(
        "Solo alertas críticas/urgentes",
        default=False,
        help_text="Obsoleto: ya no se muestra en la UI",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
        db_table = "porvoz_perfil"

    def __str__(self) -> str:
        return f"{self.user.username}"

    @property
    def plan_expira_en(self):
        """Alias legacy para compatibilidad con código antiguo."""
        return self.plan_expiration

    @plan_expira_en.setter
    def plan_expira_en(self, value):
        self.plan_expiration = value
