from django.conf import settings
from django.db import models

from apps.medicamentos.models import Medicamento
from apps.pacientes.models import Paciente


class Notificacion(models.Model):
    """
    Notificaciones internas del sistema Porvoz.

    Registra eventos de tipo sistema, recordatorio o alerta
    asociados a un usuario, paciente o medicamento.
    Las llamadas de voz se gestionarán en apps.llamadas cuando se implementen.
    """

    TIPO_RECORDATORIO = "recordatorio"
    TIPO_ALERTA = "alerta"
    TIPO_SISTEMA = "sistema"
    TIPO_CHOICES = [
        (TIPO_RECORDATORIO, "Recordatorio"),
        (TIPO_ALERTA, "Alerta"),
        (TIPO_SISTEMA, "Sistema"),
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
        default=TIPO_SISTEMA,
    )
    titulo = models.CharField("Título", max_length=200)
    mensaje = models.TextField("Mensaje", blank=True)
    fecha_programada = models.DateTimeField("Fecha programada", null=True, blank=True)
    leida = models.BooleanField("Leída", default=False)
    creado_en = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        db_table = "porvoz_notificacion"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["usuario", "leida"], name="porvoz_noti_usuario_idx"),
            models.Index(fields=["usuario", "tipo"], name="porvoz_noti_usuario_tipo_idx"),
            models.Index(fields=["paciente"], name="porvoz_noti_paciente_idx"),
            models.Index(fields=["fecha_programada"], name="porvoz_noti_fecha_pr_idx"),
        ]

    def __str__(self) -> str:
        estado = "Leída" if self.leida else "No leída"
        return f"{self.titulo} - {estado}"
