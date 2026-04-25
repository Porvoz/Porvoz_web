from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType

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
    intentos = models.PositiveSmallIntegerField("Número de intento", default=1)
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

    RESULTADO_CONFIRMADA = "confirmada"
    RESULTADO_NEGATIVA = "negativa"
    RESULTADO_DESPUES = "despues"
    RESULTADO_SIN_CONFIRMAR = "sin_confirmar"
    RESULTADO_RECHAZO = "rechazo_tratamiento"
    RESULTADO_EMERGENCIA = "emergencia"
    RESULTADO_CHOICES = [
        (RESULTADO_CONFIRMADA, "Confirmó toma"),
        (RESULTADO_NEGATIVA, "No tomó"),
        (RESULTADO_DESPUES, "Lo tomará después"),
        (RESULTADO_SIN_CONFIRMAR, "Sin confirmar"),
        (RESULTADO_RECHAZO, "Rechaza tratamiento"),
        (RESULTADO_EMERGENCIA, "Posible emergencia"),
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
    resultado = models.CharField(
        "Resultado de toma",
        max_length=20,
        choices=RESULTADO_CHOICES,
        default=RESULTADO_SIN_CONFIRMAR,
    )
    transcripcion = models.TextField("Transcripción", blank=True)
    creado_en = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Respuesta de llamada"
        verbose_name_plural = "Respuestas de llamadas"
        db_table = "porvoz_respuesta_llamada"

    def __str__(self) -> str:
        return f"Respuesta {self.como_respondio} — {self.llamada}"


class AuditoriaLog(models.Model):
    """
    Registro de cambios en cualquier modelo (Medicamento, Paciente, etc)
    """

    ACCION_CREATE = "create"
    ACCION_UPDATE = "update"
    ACCION_DELETE = "delete"
    ACCION_CHOICES = [
        (ACCION_CREATE, "Crear"),
        (ACCION_UPDATE, "Actualizar"),
        (ACCION_DELETE, "Eliminar"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias",
    )
    contenido_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Modelo afectado (Medicamento, Paciente, etc)",
    )
    objeto_id = models.PositiveIntegerField(
        help_text="ID del objeto afectado"
    )
    objeto_str = models.CharField(
        "Representación del objeto",
        max_length=255,
        blank=True,
        help_text="Nombre/descripción del objeto para legibilidad",
    )
    accion = models.CharField(
        "Acción",
        max_length=10,
        choices=ACCION_CHOICES,
    )
    cambios = models.JSONField(
        "Cambios",
        default=dict,
        blank=True,
        help_text="Para UPDATE: {campo: [valor_anterior, valor_nuevo]}",
    )
    ip_address = models.GenericIPAddressField(
        "Dirección IP",
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        "User Agent",
        blank=True,
    )
    timestamp = models.DateTimeField(
        "Timestamp",
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "Auditoría"
        verbose_name_plural = "Auditorías"
        db_table = "porvoz_auditoria"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["usuario", "timestamp"]),
            models.Index(fields=["contenido_type", "objeto_id"]),
            models.Index(fields=["accion"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_accion_display()} - {self.objeto_str} ({self.timestamp})"

    @staticmethod
    def _get_client_ip(request):
        """Obtiene IP del cliente desde request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    @classmethod
    def registrar(cls, usuario, obj, accion: str, cambios: dict = None, request=None):
        """Registra un evento de auditoría para mantener compatibilidad con servicios actuales."""
        content_type = ContentType.objects.get_for_model(obj.__class__)
        ip_address = None
        user_agent = ""

        if request is not None:
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

        return cls.objects.create(
            usuario=usuario,
            contenido_type=content_type,
            objeto_id=obj.pk,
            objeto_str=str(obj),
            accion=accion,
            cambios=cambios or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
