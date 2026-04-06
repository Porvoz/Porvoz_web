from django.db import models

from apps.pacientes.models import Paciente


class Medicamento(models.Model):
    """
    Modelo para representar un medicamento asociado a un paciente.
    Soporta múltiples horarios por día e instrucciones para llamadas con IA.
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
    dosis = models.CharField(
        "Dosis", max_length=100, help_text="Ej: 1 tableta, 500mg, etc."
    )
    frecuencia_tipo = models.CharField(
        "Tipo de frecuencia",
        max_length=20,
        choices=FRECUENCIA_CHOICES,
        default=FRECUENCIA_HORARIO,
    )
    horario = models.TimeField(
        "Horario de toma (legacy)",
        blank=True,
        null=True,
        help_text="Mantenido para compatibilidad; usar horarios cuando existan",
    )
    cada_x_horas = models.PositiveIntegerField(
        "Cada cuántas horas",
        blank=True,
        null=True,
        help_text="Para frecuencia 'Cada X horas' (ej: 8 = cada 8 horas)",
    )
    hora_inicio = models.TimeField(
        "Hora de inicio",
        blank=True,
        null=True,
        help_text="Hora de inicio para 'Cada X horas' (ej: 08:00)",
    )
    fecha_inicio_tratamiento = models.DateField(
        "Fecha de inicio del tratamiento",
        blank=True,
        null=True,
        help_text="Para 'Cada X horas': fecha desde la que se calculan las tomas",
    )
    duracion_dias = models.PositiveIntegerField(
        "Duración en días",
        blank=True,
        null=True,
        help_text="Dejar vacío para tratamiento indefinido; o indicar días (ej: 7, 30).",
    )
    instrucciones_llamada = models.TextField(
        "Instrucciones para la llamada",
        blank=True,
        help_text="Contexto para la IA: 'Recordar con el desayuno', 'Preguntar efectos'.",
    )
    minutos_antes_llamada = models.PositiveSmallIntegerField(
        "Minutos antes para llamar",
        default=0,
        blank=True,
        help_text="Llamar X minutos antes de la hora de toma (ej: 15)",
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

    def get_horarios_ordenados(self):
        """Horarios de toma ordenados (usa HorarioMedicamento o fallback a horario legacy)."""
        horarios = list(self.horarios.all().order_by("orden", "hora"))
        if horarios:
            return horarios
        if self.horario:
            # Fallback legacy: objeto mínimo con .hora para compatibilidad en templates
            return [type("LegacyH", (), {"hora": self.horario, "orden": 0})()]
        return []

    def get_primera_hora(self):
        """Primera hora de toma para mostrar (compatibilidad con vistas existentes)."""
        horarios = self.horarios.all().order_by("orden", "hora").first()
        if horarios:
            return horarios.hora
        return self.horario

    def __str__(self) -> str:
        if self.frecuencia_tipo == self.FRECUENCIA_CADA_X_HORAS:
            return f"{self.nombre} - {self.paciente.nombre} (Cada {self.cada_x_horas}h)"
        primera = self.get_primera_hora()
        return f"{self.nombre} - {self.paciente.nombre} ({primera})"


class HorarioMedicamento(models.Model):
    """Horario de toma para un medicamento (permite múltiples tomas al día)."""

    medicamento = models.ForeignKey(
        Medicamento,
        on_delete=models.CASCADE,
        related_name="horarios",
    )
    hora = models.TimeField("Hora de toma")
    orden = models.PositiveSmallIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Horario de medicamento"
        verbose_name_plural = "Horarios de medicamento"
        db_table = "porvoz_horario_medicamento"
        ordering = ["orden", "hora"]
