from django.db import models

from apps.pacientes.models import Paciente


class Medicamento(models.Model):
    """
    Modelo para representar un medicamento asociado a un paciente.
    """
    FRECUENCIA_HORARIO = "horario"
    FRECUENCIA_CADA_X_HORAS = "cada_x_horas"
    FRECUENCIA_CHOICES = [
        (FRECUENCIA_HORARIO, "Horario específico"),
        (FRECUENCIA_CADA_X_HORAS, "Cada X horas"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="medicamentos",
    )
    nombre = models.CharField("Nombre del medicamento", max_length=200)
    dosis = models.CharField("Dosis", max_length=100, help_text="Ej: 1 tableta, 500mg, etc.")
    frecuencia_tipo = models.CharField(
        "Tipo de frecuencia",
        max_length=20,
        choices=FRECUENCIA_CHOICES,
        default=FRECUENCIA_HORARIO,
    )
    horario = models.TimeField("Horario de toma", blank=True, null=True, help_text="Para frecuencia 'Horario específico'")
    cada_x_horas = models.PositiveIntegerField(
        "Cada cuántas horas",
        blank=True,
        null=True,
        help_text="Para frecuencia 'Cada X horas' (ej: 8 = cada 8 horas)"
    )
    hora_inicio = models.TimeField(
        "Hora de inicio",
        blank=True,
        null=True,
        help_text="Hora de inicio para 'Cada X horas' (ej: 08:00)"
    )
    # Duración: null = indefinido, número = cantidad de días
    duracion_dias = models.PositiveIntegerField(
        "Duración en días",
        blank=True,
        null=True,
        help_text="Dejar vacío para tratamiento indefinido; o indicar cantidad de días (ej: 7, 30)"
    )
    activo = models.BooleanField("Activo", default=True)
    creado_en = models.DateTimeField("Fecha de creación", auto_now_add=True)
    actualizado_en = models.DateTimeField("Fecha de actualización", auto_now=True)

    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"
        db_table = "porvoz_medicamento"
        indexes = [
            models.Index(fields=["paciente", "activo"]),
            models.Index(fields=["horario"]),
        ]

    def __str__(self) -> str:
        if self.frecuencia_tipo == self.FRECUENCIA_CADA_X_HORAS:
            return f"{self.nombre} - {self.paciente.nombre} (Cada {self.cada_x_horas}h)"
        return f"{self.nombre} - {self.paciente.nombre} ({self.horario})"
