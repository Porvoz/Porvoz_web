"""
Servicio para gestión de llamadas automáticas.

Responsabilidades:
- Crear llamadas programadas desde medicamentos
- Ejecutar llamadas pendientes (disparar a Twilio)
- Registrar respuestas y estado final
- Crear alertas si el paciente no responde
"""

import logging
import urllib.parse
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from apps.llamadas.models import Llamada, RespuestaLlamada
from apps.medicamentos.models import Medicamento
from apps.notificaciones.services.notificacion_service import NotificacionService
from apps.pacientes.models import Paciente

logger = logging.getLogger(__name__)


class LlamadaService:
    """Encapsula la lógica de llamadas automáticas."""

    @staticmethod
    def crear_llamada_programada(
        medicamento: Medicamento,
        usuario: User,
        paciente: Paciente,
        fecha_programada: datetime,
    ) -> Llamada:
        """
        Crea una llamada programada para un medicamento.

        Returns:
            Llamada creada con estado 'programada'
        """
        return Llamada.objects.create(
            medicamento=medicamento,
            usuario=usuario,
            paciente=paciente,
            fecha_programada=fecha_programada,
            estado=Llamada.ESTADO_PROGRAMADA,
        )

    @staticmethod
    def programar_llamadas_medicamento(medicamento, usuario) -> list:
        """
        Crea Llamadas programadas para el próximo ciclo de un medicamento.
        Cancela las llamadas 'programada' existentes antes de crear las nuevas.

        Solo actúa si el medicamento tiene instrucciones_llamada configuradas.

        Returns:
            Lista de Llamadas creadas
        """
        if not medicamento.instrucciones_llamada:
            return []

        # Cancelar llamadas programadas anteriores de este medicamento
        Llamada.objects.filter(
            medicamento=medicamento,
            estado=Llamada.ESTADO_PROGRAMADA,
        ).delete()

        ahora = timezone.now()
        hoy = ahora.date()
        offset = timedelta(minutes=medicamento.minutos_antes_llamada or 0)
        creadas = []

        if medicamento.frecuencia_tipo == medicamento.FRECUENCIA_HORARIO:
            horarios = list(medicamento.horarios.order_by("orden", "hora"))
            if not horarios and medicamento.horario:
                horarios = [type("H", (), {"hora": medicamento.horario})()]

            for h in horarios:
                dt_hoy = timezone.make_aware(datetime.combine(hoy, h.hora)) - offset
                dt_manana = dt_hoy + timedelta(days=1)
                fecha = dt_hoy if dt_hoy > ahora else dt_manana

                llamada = LlamadaService.crear_llamada_programada(
                    medicamento=medicamento,
                    usuario=usuario,
                    paciente=medicamento.paciente,
                    fecha_programada=fecha,
                )
                creadas.append(llamada)

        elif medicamento.frecuencia_tipo == medicamento.FRECUENCIA_CADA_X_HORAS:
            if medicamento.hora_inicio and medicamento.cada_x_horas:
                dt_base = timezone.make_aware(
                    datetime.combine(hoy, medicamento.hora_inicio)
                )
                intervalo = timedelta(hours=medicamento.cada_x_horas)
                # Siguiente dosis que aún no haya pasado
                dt_siguiente = dt_base
                while dt_siguiente - offset <= ahora:
                    dt_siguiente += intervalo

                llamada = LlamadaService.crear_llamada_programada(
                    medicamento=medicamento,
                    usuario=usuario,
                    paciente=medicamento.paciente,
                    fecha_programada=dt_siguiente - offset,
                )
                creadas.append(llamada)

        return creadas

    @staticmethod
    def ejecutar_llamadas_pendientes():
        """
        Busca llamadas programadas con fecha vencida y las ejecuta.
        Llamar periódicamente (cron o management command).
        """
        from apps.llamadas.services.proveedor_voz_service import ProveedorVozService

        ahora = timezone.now()
        pendientes = Llamada.objects.filter(
            estado=Llamada.ESTADO_PROGRAMADA,
            fecha_programada__lte=ahora,
        ).select_related("medicamento", "paciente", "usuario")

        if not pendientes.exists():
            logger.info("[LlamadaService] No hay llamadas pendientes.")
            return

        base_url = ProveedorVozService.get_base_url()
        logger.info(f"[LlamadaService] {pendientes.count()} llamada(s) por ejecutar.")

        for llamada in pendientes:
            paciente = llamada.paciente
            medicamento = llamada.medicamento

            numero = getattr(paciente, "telefono", None)
            if not numero:
                logger.warning(
                    f"[LlamadaService] Llamada #{llamada.id}: paciente sin teléfono."
                )
                llamada.estado = Llamada.ESTADO_FALLIDA
                llamada.save(update_fields=["estado"])
                continue

            mensaje = (
                medicamento.instrucciones_llamada
                if medicamento and medicamento.instrucciones_llamada
                else f"Recuerde tomar {medicamento.nombre if medicamento else 'su medicamento'}."
            )

            try:
                voice_url = (
                    f"{base_url}/llamadas/webhook/voice/"
                    f"?llamada_id={llamada.id}&mensaje={urllib.parse.quote(mensaje)}"
                )
                status_url = f"{base_url}/llamadas/webhook/status/"

                call_sid = ProveedorVozService.disparar_llamada(
                    numero_telefono=numero,
                    mensaje=mensaje,
                    voice_url=voice_url,
                    status_url=status_url,
                )

                llamada.call_sid = call_sid
                llamada.estado = Llamada.ESTADO_EN_CURSO
                llamada.fecha_ejecutada = timezone.now()
                llamada.save(update_fields=["call_sid", "estado", "fecha_ejecutada"])

            except Exception as e:
                logger.error(
                    f"[LlamadaService] Error ejecutando llamada #{llamada.id}: {e}"
                )
                llamada.estado = Llamada.ESTADO_FALLIDA
                llamada.save(update_fields=["estado"])
                LlamadaService._crear_alerta_fallo(llamada, str(e))

    @staticmethod
    def registrar_respuesta(
        call_sid: str, transcripcion: str, como_respondio: str
    ) -> RespuestaLlamada:
        """
        Registra la respuesta del paciente a una llamada.

        Args:
            call_sid: ID de Twilio
            transcripcion: Conversación completa
            como_respondio: 'atendida' | 'no_atendida' | 'buzon'

        Returns:
            RespuestaLlamada creada
        """
        llamada = Llamada.objects.filter(call_sid=call_sid).first()
        if not llamada:
            logger.warning(
                f"[LlamadaService] No se encontró llamada con call_sid={call_sid}"
            )
            return None

        respuesta, _ = RespuestaLlamada.objects.update_or_create(
            llamada=llamada,
            defaults={
                "como_respondio": como_respondio,
                "transcripcion": transcripcion,
            },
        )

        if como_respondio in (
            RespuestaLlamada.RESPUESTA_NO_ATENDIDA,
            RespuestaLlamada.RESPUESTA_BUZON,
        ):
            LlamadaService._crear_alerta_no_atendida(llamada)

        return respuesta

    @staticmethod
    def registrar_estado_final(call_sid: str, estado_twilio: str, duracion: int = None):
        """
        Actualiza estado y duración de la llamada cuando Twilio envía el webhook de status.

        Args:
            call_sid: ID de Twilio
            estado_twilio: Estado reportado por Twilio (completed, busy, no-answer, failed…)
            duracion: Duración en segundos
        """
        llamada = Llamada.objects.filter(call_sid=call_sid).first()
        if not llamada:
            return

        mapa_estado = {
            "completed": Llamada.ESTADO_COMPLETADA,
            "busy": Llamada.ESTADO_FALLIDA,
            "no-answer": Llamada.ESTADO_FALLIDA,
            "failed": Llamada.ESTADO_FALLIDA,
            "canceled": Llamada.ESTADO_FALLIDA,
        }
        nuevo_estado = mapa_estado.get(estado_twilio, Llamada.ESTADO_COMPLETADA)

        campos = {"estado": nuevo_estado}
        if duracion is not None:
            campos["duracion"] = duracion

        Llamada.objects.filter(pk=llamada.pk).update(**campos)

        if nuevo_estado == Llamada.ESTADO_FALLIDA and not hasattr(
            llamada, "_alerta_creada"
        ):
            llamada.refresh_from_db()
            if not RespuestaLlamada.objects.filter(llamada=llamada).exists():
                LlamadaService._crear_alerta_no_atendida(llamada)

    # ------------------------------------------------------------------
    # Privados
    # ------------------------------------------------------------------

    @staticmethod
    def _crear_alerta_no_atendida(llamada: Llamada):
        med_nombre = (
            llamada.medicamento.nombre if llamada.medicamento else "medicamento"
        )
        NotificacionService.crear_notificacion_alerta(
            usuario=llamada.usuario,
            titulo=f"Llamada no atendida — {med_nombre}",
            mensaje=(
                f"{llamada.paciente.nombre} no respondió la llamada de recordatorio "
                f"para {med_nombre}."
            ),
            paciente=llamada.paciente,
            medicamento=llamada.medicamento,
        )

    @staticmethod
    def _crear_alerta_fallo(llamada: Llamada, error: str):
        med_nombre = (
            llamada.medicamento.nombre if llamada.medicamento else "medicamento"
        )
        NotificacionService.crear_notificacion_alerta(
            usuario=llamada.usuario,
            titulo=f"Error en llamada — {med_nombre}",
            mensaje=f"No se pudo realizar la llamada a {llamada.paciente.nombre}: {error}",
            paciente=llamada.paciente,
            medicamento=llamada.medicamento,
        )
