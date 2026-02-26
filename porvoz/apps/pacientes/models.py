from django.conf import settings
from django.db import models


def _get_perfil_for_user(user):
    """Obtiene el perfil del usuario si existe (evita import circular)."""
    try:
        return user.perfil
    except Exception:
        return None


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

    def get_display_nombre(self):
        """Nombre a mostrar: del perfil cuando es el usuario mismo, sino el del paciente."""
        if not self.es_usuario_mismo:
            return self.nombre
        perfil = _get_perfil_for_user(self.usuario)
        if perfil:
            name = f"{perfil.first_name or ''} {perfil.last_name or ''}".strip()
            if name:
                return name
        name = f"{self.usuario.first_name or ''} {self.usuario.last_name or ''}".strip()
        return name or self.nombre

    def get_display_foto(self):
        """Foto a mostrar: del perfil cuando es el usuario mismo, sino la del paciente."""
        if not self.es_usuario_mismo:
            return self.foto
        perfil = _get_perfil_for_user(self.usuario)
        if perfil and perfil.profile_image:
            return perfil.profile_image
        return self.foto

    def get_display_telefono(self):
        """Teléfono a mostrar: del perfil cuando es el usuario mismo, sino el del paciente."""
        if not self.es_usuario_mismo:
            return self.telefono
        perfil = _get_perfil_for_user(self.usuario)
        if perfil and perfil.phone:
            return perfil.phone
        return self.telefono

    def get_display_fecha_nacimiento(self):
        """Fecha de nacimiento a mostrar: del perfil cuando es el usuario mismo."""
        if not self.es_usuario_mismo:
            return self.fecha_nacimiento
        perfil = _get_perfil_for_user(self.usuario)
        if perfil and perfil.date_of_birth:
            return perfil.date_of_birth
        return self.fecha_nacimiento


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
