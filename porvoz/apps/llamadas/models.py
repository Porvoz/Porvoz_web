from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.pacientes.models import Paciente
from apps.medicamentos.models import Medicamento


class Notificacion(models.Model):
    """
    Modelo para representar notificaciones/llamadas realizadas.
    """
    TIPO_LLAMADA = "llamada"
    TIPO_RECORDATORIO = "recordatorio"
    TIPO_ALERTA = "alerta"
    TIPO_SISTEMA = "sistema"
    TIPO_CHOICES = [
        (TIPO_LLAMADA, "Llamada"),
        (TIPO_RECORDATORIO, "Recordatorio"),
        (TIPO_ALERTA, "Alerta"),
        (TIPO_SISTEMA, "Sistema"),
    ]

    ESTADO_PENDIENTE = "pendiente"
    ESTADO_ENVIADA = "enviada"
    ESTADO_ATENDIDA = "atendida"
    ESTADO_NO_ATENDIDA = "no_atendida"
    ESTADO_FALLIDA = "fallida"
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_ENVIADA, "Enviada"),
        (ESTADO_ATENDIDA, "Atendida"),
        (ESTADO_NO_ATENDIDA, "No atendida"),
        (ESTADO_FALLIDA, "Fallida"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="notificaciones",
        null=True,
        blank=True,
    )
    medicamento = models.ForeignKey(
        Medicamento,
        on_delete=models.SET_NULL,
        related_name="notificaciones",
        null=True,
        blank=True,
    )
    tipo = models.CharField(
        "Tipo de notificación",
        max_length=20,
        choices=TIPO_CHOICES,
        default=TIPO_LLAMADA,
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
    )
    titulo = models.CharField("Título", max_length=200)
    mensaje = models.TextField("Mensaje", blank=True)
    fecha_programada = models.DateTimeField("Fecha programada", null=True, blank=True)
    fecha_enviada = models.DateTimeField("Fecha enviada", null=True, blank=True)
    fecha_atendida = models.DateTimeField("Fecha atendida", null=True, blank=True)
    leida = models.BooleanField("Leída", default=False)
    creado_en = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        db_table = "porvoz_notificacion"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["usuario", "leida"]),
            models.Index(fields=["usuario", "tipo"]),
            models.Index(fields=["paciente"]),
            models.Index(fields=["fecha_programada"]),
        ]

    def __str__(self) -> str:
        return f"{self.titulo} - {self.get_estado_display()}"
