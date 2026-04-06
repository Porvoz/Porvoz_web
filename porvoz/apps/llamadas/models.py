from django.conf import settings
from django.db import models

from apps.medicamentos.models import Medicamento
from apps.pacientes.models import Paciente


class Llamada(models.Model):
    """
    Registro de una llamada automática programada o ejecutada.
    Una llamada se origina desde un medicamento con instrucciones_llamada configuradas.
    """

    ESTADO_PROGRAMADA = "programada"
    ESTADO_EN_CURSO = "en_curso"
    ESTADO_COMPLETADA = "completada"
    ESTADO_FALLIDA = "fallida"
    ESTADO_CHOICES = [
        (ESTADO_PROGRAMADA, "Programada"),
        (ESTADO_EN_CURSO, "En curso"),
        (ESTADO_COMPLETADA, "Completada"),
        (ESTADO_FALLIDA, "Fallida"),
    ]

    medicamento = models.ForeignKey(
        Medicamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="llamadas",
        verbose_name="Medicamento",
    )
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="llamadas",
        verbose_name="Paciente",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="llamadas",
        verbose_name="Usuario",
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PROGRAMADA,
    )
    fecha_programada = models.DateTimeField("Fecha programada")
    fecha_ejecutada = models.DateTimeField("Fecha ejecutada", null=True, blank=True)
    call_sid = models.CharField(
        "ID de llamada (Twilio)",
        max_length=100,
        blank=True,
        db_index=True,
    )
    duracion = models.PositiveIntegerField("Duración (segundos)", null=True, blank=True)
    creado_en = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Llamada"
        verbose_name_plural = "Llamadas"
        db_table = "porvoz_llamada"
        ordering = ["-fecha_programada"]
        indexes = [
            models.Index(fields=["usuario", "estado"], name="porvoz_llam_usuario_idx"),
            models.Index(fields=["paciente"], name="porvoz_llam_paciente_idx"),
            models.Index(fields=["fecha_programada"], name="porvoz_llam_fecha_idx"),
        ]

    def __str__(self) -> str:
        med = self.medicamento.nombre if self.medicamento else "Sin medicamento"
        return f"Llamada {med} — {self.paciente.nombre} ({self.estado})"


class RespuestaLlamada(models.Model):
    """
    Respuesta del paciente a una llamada automática.
    Se crea cuando Twilio envía el webhook de finalización.
    """

    RESPUESTA_ATENDIDA = "atendida"
    RESPUESTA_NO_ATENDIDA = "no_atendida"
    RESPUESTA_BUZON = "buzon"
    RESPUESTA_CHOICES = [
        (RESPUESTA_ATENDIDA, "Atendida"),
        (RESPUESTA_NO_ATENDIDA, "No atendida"),
        (RESPUESTA_BUZON, "Buzón de voz"),
    ]

    llamada = models.OneToOneField(
        Llamada,
        on_delete=models.CASCADE,
        related_name="respuesta",
        verbose_name="Llamada",
    )
    como_respondio = models.CharField(
        "Cómo respondió",
        max_length=20,
        choices=RESPUESTA_CHOICES,
    )
    transcripcion = models.TextField("Transcripción", blank=True)
    creado_en = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Respuesta de llamada"
        verbose_name_plural = "Respuestas de llamadas"
        db_table = "porvoz_respuesta_llamada"

    def __str__(self) -> str:
        return f"Respuesta {self.como_respondio} — {self.llamada}"
