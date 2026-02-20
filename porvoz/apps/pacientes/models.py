from django.conf import settings
from django.db import models


class Paciente(models.Model):
    """
    Modelo para representar un paciente.
    Un paciente puede ser el mismo usuario o otra persona agregada por el usuario.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pacientes",
    )
    nombre = models.CharField("Nombre completo", max_length=200)
    telefono = models.CharField("Teléfono", max_length=30)
    es_usuario_mismo = models.BooleanField(
        "Es el usuario mismo",
        default=False,
        help_text="True si este paciente es el mismo usuario que lo creó"
    )
    fecha_nacimiento = models.DateField("Fecha de nacimiento", blank=True, null=True)
    foto = models.ImageField("Foto del paciente", upload_to="pacientes_fotos/", blank=True, null=True)
    descripcion = models.TextField("Descripción", blank=True, help_text="Información adicional sobre el paciente")
    notas = models.TextField("Notas adicionales", blank=True)
    activo = models.BooleanField("Activo", default=True)
    creado_en = models.DateTimeField("Fecha de creación", auto_now_add=True)
    actualizado_en = models.DateTimeField("Fecha de actualización", auto_now=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        db_table = "porvoz_paciente"
        unique_together = [["usuario", "telefono"]]
        indexes = [
            models.Index(fields=["usuario", "activo"]),
        ]

    def __str__(self) -> str:
        tipo = "Yo" if self.es_usuario_mismo else "Otro"
        return f"{self.nombre} ({tipo}) - {self.usuario.username}"


class Enfermedad(models.Model):
    """
    Modelo para representar una enfermedad o condición médica de un paciente.
    """
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="enfermedades",
    )
    nombre = models.CharField("Nombre de la enfermedad", max_length=200)
    descripcion = models.TextField("Descripción", blank=True)
    diagnostico_fecha = models.DateField("Fecha de diagnóstico", blank=True, null=True)
    activa = models.BooleanField("Activa", default=True)
    creado_en = models.DateTimeField("Fecha de creación", auto_now_add=True)
    actualizado_en = models.DateTimeField("Fecha de actualización", auto_now=True)

    class Meta:
        verbose_name = "Enfermedad"
        verbose_name_plural = "Enfermedades"
        db_table = "porvoz_enfermedad"
        indexes = [
            models.Index(fields=["paciente", "activa"]),
        ]

    def __str__(self) -> str:
        return f"{self.nombre} - {self.paciente.nombre}"
