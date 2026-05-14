"""
Admin panel models for código de acceso, payment history, y support tickets.
"""

import secrets
import string
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models

from apps.core.models import Perfil

# Costo mensual estimado por plan (Twilio $80/llamada + infra $4.000)
COSTO_MENSUAL_PLAN = {
    Perfil.PLAN_FREEMIUM:        1_200 + 4_000,   # 15 llamadas
    Perfil.PLAN_GROWTH:          7_200 + 4_000,   # 90 llamadas
    Perfil.PLAN_MULTI_BUSINESS: 24_000 + 4_000,   # 300 llamadas
    Perfil.PLAN_PROFESIONAL:    72_000 + 4_000,   # 900 llamadas
}


class CodigoAcceso(models.Model):
    """Código para dar acceso a planes específicos sin pasarela de pagos"""

    ESTADO_DISPONIBLE = "disponible"
    ESTADO_USADO = "usado"
    ESTADO_EXPIRADO = "expirado"
    ESTADO_CANCELADO = "cancelado"

    ESTADO_CHOICES = [
        (ESTADO_DISPONIBLE, "Disponible"),
        (ESTADO_USADO, "Usado"),
        (ESTADO_EXPIRADO, "Expirado"),
        (ESTADO_CANCELADO, "Cancelado"),
    ]

    # Código único (ej: PROMO-ABC123-XYZ)
    codigo = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    # Qué plan accede
    plan = models.CharField(
        max_length=20,
        choices=Perfil.PLAN_CHOICES,
        help_text="Plan que otorga este código",
    )

    # Duración en meses
    duracion_meses = models.IntegerField(
        default=1,
        choices=[(1, "1 mes"), (3, "3 meses"), (6, "6 meses"), (12, "1 año")],
    )

    # Estado del código
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_DISPONIBLE,
    )

    # Quién lo usó
    usuario_usado_por = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="codigos_usados",
    )

    # Fechas
    creado_en = models.DateTimeField(auto_now_add=True)
    usado_en = models.DateTimeField(null=True, blank=True)
    expira_en = models.DateTimeField(null=True, blank=True)
    # Ventana para canjearlo: el plan empieza CUANDO se usa, no cuando se crea
    fecha_limite_canje = models.DateField(
        null=True, blank=True,
        help_text="Fecha límite para canjear este código. El plan empieza al canjearlo.",
    )

    # Notas
    notas = models.TextField(blank=True)

    # Quién creó el código (admin)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="codigos_creados",
        limit_choices_to={"is_staff": True},
    )

    class Meta:
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["estado"]),
        ]

    def __str__(self):
        return f"{self.codigo} ({self.plan}) - {self.estado}"

    @property
    def fecha_expiracion(self):
        """Retorna la fecha de expiración calculada"""
        if self.expira_en:
            return self.expira_en
        # Si no está seteada, la calculamos
        return self.creado_en + timedelta(days=self.duracion_meses * 30)

    @staticmethod
    def generar_codigo():
        """Genera un código único: PROMO-ABC123-XYZ"""
        chars = string.ascii_uppercase + string.digits
        while True:
            parte1 = "PROMO"
            parte2 = "".join(secrets.choice(chars) for _ in range(6))
            parte3 = "".join(secrets.choice(chars) for _ in range(3))
            codigo = f"{parte1}-{parte2}-{parte3}"
            if not CodigoAcceso.objects.filter(codigo=codigo).exists():
                return codigo


class PagoHistorico(models.Model):
    """Registro de todos los pagos/cambios de plan"""

    TIPO_CODIGO = "codigo"
    TIPO_TRANSFERENCIA = "transferencia"
    TIPO_GRATUITO = "gratuito"
    TIPO_PROMOCION = "promocion"

    TIPO_CHOICES = [
        (TIPO_CODIGO, "Código de acceso"),
        (TIPO_TRANSFERENCIA, "Transferencia bancaria"),
        (TIPO_GRATUITO, "Acceso gratuito"),
        (TIPO_PROMOCION, "Promoción"),
    ]

    METODO_BANCOLOMBIA = "bancolombia"
    METODO_NEQUI = "nequi"
    METODO_EFECTIVO = "efectivo"
    METODO_OTRO = "otro"

    METODO_CHOICES = [
        (METODO_BANCOLOMBIA, "Bancolombia"),
        (METODO_NEQUI, "Nequi"),
        (METODO_EFECTIVO, "Efectivo"),
        (METODO_OTRO, "Otro"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pagos_historico",
    )

    # Qué plan se le asignó
    plan = models.CharField(
        max_length=20,
        choices=Perfil.PLAN_CHOICES,
    )

    # Duración en meses
    duracion_meses = models.IntegerField()

    # Tipo de pago
    tipo_pago = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
    )

    # Código usado (si es de tipo CODIGO)
    codigo_usado = models.ForeignKey(
        CodigoAcceso,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # Comprobante de pago (imagen/PDF para pagos manuales)
    comprobante = models.FileField(
        upload_to="comprobantes_pago/",
        null=True,
        blank=True,
    )

    # Método específico de transferencia
    metodo_transferencia = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        blank=True,
    )

    # Monto pagado (si es transferencia)
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monto en COP",
    )

    # Referencia de transferencia
    referencia_pago = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ej: número de comprobante de transferencia",
    )

    # Fecha de pago
    fecha_pago = models.DateTimeField(auto_now_add=True)

    # Fecha hasta cuándo es válido el plan
    fecha_hasta = models.DateField()

    # Costos y ganancia (calculados al guardar)
    costo_estimado = models.DecimalField(
        max_digits=10, decimal_places=0, null=True, blank=True,
        help_text="Costo Twilio + infra estimado en COP",
    )
    ganancia_neta = models.DecimalField(
        max_digits=10, decimal_places=0, null=True, blank=True,
        help_text="monto − costo_estimado",
    )

    # Notas
    notas = models.TextField(blank=True)

    # Procesado por (admin)
    procesado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="pagos_procesados",
        limit_choices_to={"is_staff": True},
    )

    class Meta:
        ordering = ["-fecha_pago"]

    def save(self, *args, **kwargs):
        # Leer costo de ConfiguracionPlan o usar fallback
        try:
            config = ConfiguracionPlan.objects.get(plan=self.plan)
            costo_mes = int(config.costo_estimado)
        except ConfiguracionPlan.DoesNotExist:
            costo_mes = COSTO_MENSUAL_PLAN.get(self.plan, 0)

        self.costo_estimado = costo_mes * self.duracion_meses
        if self.monto:
            self.ganancia_neta = int(self.monto) - int(self.costo_estimado)
        else:
            self.ganancia_neta = -int(self.costo_estimado)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.username} - {self.plan} ({self.tipo_pago})"


class TicketSoporte(models.Model):
    """Tickets de soporte de usuarios"""

    PRIORIDAD_BAJA = "baja"
    PRIORIDAD_MEDIA = "media"
    PRIORIDAD_ALTA = "alta"

    PRIORIDAD_CHOICES = [
        (PRIORIDAD_BAJA, "Baja"),
        (PRIORIDAD_MEDIA, "Media"),
        (PRIORIDAD_ALTA, "Alta"),
    ]

    ESTADO_ABIERTO = "abierto"
    ESTADO_EN_PROGRESO = "en_progreso"
    ESTADO_RESUELTO = "resuelto"
    ESTADO_CERRADO = "cerrado"

    ESTADO_CHOICES = [
        (ESTADO_ABIERTO, "Abierto"),
        (ESTADO_EN_PROGRESO, "En progreso"),
        (ESTADO_RESUELTO, "Resuelto"),
        (ESTADO_CERRADO, "Cerrado"),
    ]

    # Puede ser null para tickets de visitantes sin cuenta
    usuario = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tickets",
    )

    # Datos de contacto (para visitantes sin cuenta o complemento)
    nombre_contacto = models.CharField(max_length=150, blank=True)
    email_contacto = models.EmailField(blank=True)
    telefono_contacto = models.CharField(max_length=30, blank=True)

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()

    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default=PRIORIDAD_MEDIA,
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ABIERTO,
    )

    asignado_a = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tickets_asignados",
        limit_choices_to={"is_staff": True},
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    resuelto_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        nombre = self.usuario.username if self.usuario else self.nombre_contacto or "Anónimo"
        return f"{self.titulo} ({nombre})"

    @property
    def remitente(self):
        if self.usuario:
            return self.usuario.get_full_name() or self.usuario.username
        return self.nombre_contacto or "Visitante"

    @property
    def email_remitente(self):
        if self.usuario:
            return self.usuario.email
        return self.email_contacto


class MensajeTicket(models.Model):
    """Mensajes de chat dentro de un ticket de soporte"""

    ticket = models.ForeignKey(
        TicketSoporte,
        on_delete=models.CASCADE,
        related_name="mensajes",
    )
    # Null si es del visitante que no tiene cuenta
    autor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mensajes_soporte",
    )
    es_admin = models.BooleanField(default=False)
    contenido = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado_en"]

    def __str__(self):
        quien = "Admin" if self.es_admin else "Usuario"
        return f"[{quien}] {self.ticket.titulo[:30]}"


class ConfiguracionPlan(models.Model):
    """Configuración de planes: precios, costos, límites (editable por admin)"""

    plan = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Clave interna del plan (slug único, ej: plan_empresa)",
    )
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre del plan (Gratuito, Básico, Familiar, Profesional)",
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción breve del plan",
    )
    precio_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        help_text="Precio mensual en COP que cobra el usuario",
    )
    costo_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        help_text="Costo estimado mensual (Twilio + infraestructura)",
    )
    limite_pacientes = models.IntegerField(
        default=1,
        help_text="Cantidad máxima de pacientes",
    )
    limite_medicamentos = models.IntegerField(
        null=True,
        blank=True,
        help_text="Máximo medicamentos por paciente (null = ilimitado)",
    )
    limite_llamadas_mes = models.IntegerField(
        default=15,
        help_text="Máximo de llamadas automatizadas por mes",
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si es False, este plan no aparece en el login",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["precio_mensual"]
        verbose_name = "Configuración de Plan"
        verbose_name_plural = "Configuraciones de Planes"

    def margen_neto(self):
        """Calcula el margen neto del plan"""
        if self.precio_mensual == 0:
            return 0
        return int(self.precio_mensual) - int(self.costo_estimado)

    def porcentaje_margen(self):
        """Porcentaje de margen"""
        if self.precio_mensual == 0:
            return 0
        return round((self.margen_neto() / int(self.precio_mensual)) * 100, 1)

    def __str__(self):
        return f"{self.nombre} (${self.precio_mensual:,.0f} COP)"
