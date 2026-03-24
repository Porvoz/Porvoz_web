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
    SEXO_MUJER = "M"
    SEXO_HOMBRE = "H"
    SEXO_CHOICES = [
        (SEXO_MUJER, "Mujer"),
        (SEXO_HOMBRE, "Hombre"),
    ]
    nombre = models.CharField("Nombre completo", max_length=200)
    telefono = models.CharField("Teléfono", max_length=30)
    sexo = models.CharField(
        "Sexo",
        max_length=1,
        choices=SEXO_CHOICES,
        blank=True,
    )
    es_usuario_mismo = models.BooleanField(
        "Es el usuario mismo",
        default=False,
        help_text="True si este paciente es el mismo usuario que lo creó"
    )
    fecha_nacimiento = models.DateField("Fecha de nacimiento", blank=True, null=True)
    parentesco = models.CharField(
        "Parentesco / Relación",
        max_length=50,
        blank=True,
        help_text="Ej: Padre, Madre, Hijo/a, Cónyuge, etc."
    )
    foto = models.ImageField("Foto del paciente", upload_to="pacientes_fotos/", blank=True, null=True)
    descripcion = models.TextField("Descripción", blank=True, help_text="Información adicional sobre el paciente")
    notas = models.TextField("Notas adicionales", blank=True)
    timezone = models.CharField(
        "Zona horaria",
        max_length=50,
        default="America/Bogota",
        blank=True,
        help_text="Ej: America/Bogota, America/Mexico_City. Para programar llamadas en la hora local del paciente."
    )
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

    def get_edad_display(self):
        """Edad en años para mostrar (desde fecha de nacimiento), o None si no hay."""
        from datetime import date
        fn = self.get_display_fecha_nacimiento()
        if not fn:
            return None
        hoy = date.today()
        return hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))

    def get_primera_condicion(self):
        """Primera enfermedad activa para mostrar como condición en el panel."""
        primera = self.enfermedades.filter(activa=True).first()
        return primera.nombre if primera else None

    def get_condiciones_activas(self):
        """Lista de condiciones/enfermedades activas del paciente."""
        return [e.nombre for e in self.enfermedades.all() if e.activa]

    def get_inicio_tratamiento(self):
        """Fecha de inicio del tratamiento: creado_en del medicamento más antiguo."""
        med = self.medicamentos.filter(activo=True).order_by("creado_en").first()
        return med.creado_en.date() if med else None

    def get_fin_tratamiento(self):
        """Fecha de fin del tratamiento: max(creado_en + duracion_dias) si hay duración."""
        from datetime import timedelta
        fechas_fin = []
        for m in self.medicamentos.filter(activo=True):
            if m.duracion_dias and m.creado_en:
                fin = m.creado_en.date() + timedelta(days=m.duracion_dias)
                fechas_fin.append(fin)
        return max(fechas_fin) if fechas_fin else None


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
