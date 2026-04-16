"""
Servicio para gestión de llamadas automáticas.

Responsabilidades:
- Crear llamadas programadas desde medicamentos
- Ejecutar llamadas pendientes (disparar a Twilio)
- Registrar respuestas y estado final
- Crear alertas si el paciente no responde
"""

import logging
import re
import urllib.parse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.contrib.auth.models import User
from django.utils import timezone

from apps.llamadas.models import Llamada, RespuestaLlamada, AuditoriaLog
from apps.medicamentos.models import Medicamento
from apps.notificaciones.services.notificacion_service import NotificacionService
from apps.notificaciones.services.email_service import EmailService
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

        Returns:
            Lista de Llamadas creadas
        """
        # Cancelar llamadas programadas anteriores de este medicamento
        Llamada.objects.filter(
            medicamento=medicamento,
            estado=Llamada.ESTADO_PROGRAMADA,
        ).delete()

        ahora = timezone.now()
        hoy = timezone.localtime(ahora).date()  # fecha en hora local (Bogotá), no UTC
        offset = timedelta(minutes=medicamento.minutos_antes_llamada or 0)
        creadas = []

        if medicamento.frecuencia_tipo == medicamento.FRECUENCIA_HORARIO:
            horarios = list(medicamento.horarios.order_by("orden", "hora"))
            if not horarios and medicamento.horario:
                horarios = [type("H", (), {"hora": medicamento.horario})()]

            for h in horarios:
                hora = LlamadaService._as_time(h.hora)
                if hora is None:
                    continue
                dt_toma_hoy = timezone.make_aware(datetime.combine(hoy, hora))
                dt_hoy = dt_toma_hoy - offset
                dt_manana = dt_toma_hoy + timedelta(days=1) - offset

                if dt_toma_hoy > ahora:
                    # La hora de toma aún no llegó — llamar lo antes posible
                    fecha = max(dt_hoy, ahora + timedelta(minutes=1))
                else:
                    # La hora de toma ya pasó hoy — programar para mañana
                    fecha = dt_manana

                llamada = LlamadaService.crear_llamada_programada(
                    medicamento=medicamento,
                    usuario=usuario,
                    paciente=medicamento.paciente,
                    fecha_programada=fecha,
                )
                creadas.append(llamada)

        elif medicamento.frecuencia_tipo == medicamento.FRECUENCIA_CADA_X_HORAS:
            hora_inicio = LlamadaService._as_time(medicamento.hora_inicio)
            if hora_inicio and medicamento.cada_x_horas:
                dt_base = timezone.make_aware(
                    datetime.combine(hoy, hora_inicio)
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
    def ejecutar_llamadas_pendientes(max_workers=5):
        """
        Busca llamadas programadas con fecha vencida y las ejecuta EN PARALELO.
        Usa ThreadPoolExecutor para disparar múltiples llamadas simultáneamente.

        Args:
            max_workers: Máximo de llamadas paralelas (default 5)
        """
        from apps.llamadas.services.proveedor_voz_service import ProveedorVozService

        ahora = timezone.now()
        pendientes = list(
            Llamada.objects.filter(
                estado=Llamada.ESTADO_PROGRAMADA,
                fecha_programada__lte=ahora,
            ).select_related("medicamento", "paciente", "usuario")
        )

        if not pendientes:
            logger.info("[LlamadaService] No hay llamadas pendientes.")
            return

        base_url = ProveedorVozService.get_base_url()
        logger.info(
            f"[LlamadaService] {len(pendientes)} llamada(s) por ejecutar "
            f"(máx {max_workers} en paralelo)."
        )

        # Procesar en paralelo
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    LlamadaService._ejecutar_llamada_individual, llamada, base_url
                ): llamada
                for llamada in pendientes
            }

            for future in as_completed(futures):
                llamada = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(
                        f"[LlamadaService] Error ejecutando llamada #{llamada.id}: {e}"
                    )

    @staticmethod
    def _ejecutar_llamada_individual(llamada: Llamada, base_url: str):
        """
        Ejecuta UNA llamada (usado por ThreadPoolExecutor).
        Se ejecuta en un thread separado.
        """
        from apps.llamadas.services.proveedor_voz_service import ProveedorVozService

        llamada = Llamada.objects.select_related(
            "medicamento", "paciente", "usuario"
        ).get(pk=llamada.pk)

        paciente = llamada.paciente
        medicamento = llamada.medicamento

        # Verificar límite de llamadas del plan antes de ejecutar
        from apps.usuarios.services.planes_service import PlanService
        puede, error_plan = PlanService.puede_realizar_llamada(llamada.usuario)
        if not puede:
            logger.warning(
                f"[LlamadaService] Llamada #{llamada.id} bloqueada por límite de plan: {error_plan}"
            )
            llamada.estado = Llamada.ESTADO_FALLIDA
            llamada.save(update_fields=["estado"])
            LlamadaService._crear_alerta_fallo(llamada, error_plan)
            return

        numero = getattr(paciente, "telefono", None)
        if not numero:
            logger.warning(
                f"[LlamadaService] Llamada #{llamada.id}: paciente sin teléfono."
            )
            llamada.estado = Llamada.ESTADO_FALLIDA
            llamada.save(update_fields=["estado"])
            return

        nombre_med      = medicamento.nombre if medicamento else "su medicamento"
        instrucciones   = LlamadaService._sanitizar_mensaje(
            medicamento.instrucciones_llamada
            if medicamento and medicamento.instrucciones_llamada
            else ""
        )
        nombre_paciente = paciente.nombre if paciente else ""

        try:
            voice_url = (
                f"{base_url}/llamadas/webhook/voice/"
                f"?llamada_id={llamada.id}"
                f"&nombre_med={urllib.parse.quote(nombre_med)}"
                f"&instrucciones={urllib.parse.quote(instrucciones)}"
                f"&nombre_paciente={urllib.parse.quote(nombre_paciente)}"
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

            # Registrar auditoría
            AuditoriaLog.registrar(
                usuario=llamada.usuario,
                obj=llamada,
                accion=AuditoriaLog.ACCION_UPDATE,
                cambios={"estado": ["programada", "en_curso"], "call_sid": call_sid},
            )

        except Exception as e:
            logger.error(
                f"[LlamadaService] Error ejecutando llamada #{llamada.id}: {e}"
            )
            llamada.estado = Llamada.ESTADO_FALLIDA
            llamada.save(update_fields=["estado"])
            LlamadaService._crear_alerta_fallo(llamada, str(e))

    @staticmethod
    def registrar_respuesta(
        call_sid: str,
        transcripcion: str,
        como_respondio: str,
        resultado: str = None,
        palabras_paciente: str = "",
    ) -> RespuestaLlamada:
        """
        Registra la respuesta del paciente a una llamada.

        Args:
            call_sid: ID de Twilio
            transcripcion: Conversación completa
            como_respondio: 'atendida' | 'no_atendida' | 'buzon'
            resultado: 'confirmada' | 'negativa' | 'despues' | 'sin_confirmar'
            palabras_paciente: Lo que dijo el paciente (para notificaciones enriquecidas)

        Returns:
            RespuestaLlamada creada o actualizada
        """
        llamada = Llamada.objects.filter(call_sid=call_sid).first()
        if not llamada:
            logger.warning(
                f"[LlamadaService] No se encontró llamada con call_sid={call_sid}"
            )
            return None

        resultado_final = resultado or RespuestaLlamada.RESULTADO_SIN_CONFIRMAR

        respuesta, _ = RespuestaLlamada.objects.update_or_create(
            llamada=llamada,
            defaults={
                "como_respondio": como_respondio,
                "resultado": resultado_final,
                "transcripcion": transcripcion,
            },
        )

        if como_respondio in (
            RespuestaLlamada.RESPUESTA_NO_ATENDIDA,
            RespuestaLlamada.RESPUESTA_BUZON,
        ):
            LlamadaService._crear_alerta_no_atendida(llamada)
            LlamadaService._intentar_reintento(llamada)
        elif como_respondio == RespuestaLlamada.RESPUESTA_ATENDIDA:
            if resultado_final == RespuestaLlamada.RESULTADO_CONFIRMADA:
                LlamadaService._crear_notif_confirmada(llamada)
            elif resultado_final == RespuestaLlamada.RESULTADO_NEGATIVA:
                LlamadaService._crear_alerta_no_tomo(llamada, palabras_paciente)
                LlamadaService._intentar_reintento(llamada)
            elif resultado_final == RespuestaLlamada.RESULTADO_DESPUES:
                LlamadaService._crear_alerta_despues(llamada, palabras_paciente)
                LlamadaService._intentar_reintento(llamada)

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
    def _as_time(valor):
        """
        Convierte un valor a datetime.time de forma segura.
        Acepta datetime.time (ya correcto) o string "HH:MM" (viene de formularios POST).
        Retorna None si el valor no es convertible.
        """
        import datetime as _dt
        if valor is None:
            return None
        if isinstance(valor, _dt.time):
            return valor
        if isinstance(valor, str):
            for fmt in ("%H:%M:%S", "%H:%M"):
                try:
                    return _dt.datetime.strptime(valor.strip(), fmt).time()
                except ValueError:
                    continue
        return None

    @staticmethod
    def _sanitizar_mensaje(texto: str) -> str:
        """Trunca y elimina patrones de prompt injection básicos."""
        texto = texto[:200]
        texto = re.sub(
            r"(ignora|olvida|system\s*prompt|instrucciones anteriores|forget|override)",
            "",
            texto,
            flags=re.IGNORECASE,
        )
        return texto.strip()

    @staticmethod
    def _intentar_reintento(llamada: Llamada):
        """
        Crea una nueva Llamada programada si el medicamento permite más reintentos.
        Cuando se agotan los reintentos, dispara alerta de escalada.
        """
        medicamento = llamada.medicamento
        if not medicamento:
            return

        max_reintentos = medicamento.max_reintentos
        if max_reintentos == 0:
            return

        if llamada.intentos <= max_reintentos:
            minutos = medicamento.minutos_entre_reintentos or 30
            nueva_fecha = timezone.now() + timedelta(minutes=minutos)
            Llamada.objects.create(
                medicamento=medicamento,
                usuario=llamada.usuario,
                paciente=llamada.paciente,
                fecha_programada=nueva_fecha,
                estado=Llamada.ESTADO_PROGRAMADA,
                intentos=llamada.intentos + 1,
            )
            logger.info(
                f"[LlamadaService] Reintento #{llamada.intentos + 1} programado "
                f"en {minutos} min para llamada #{llamada.id}."
            )
        else:
            LlamadaService._crear_alerta_escalada(llamada)

    @staticmethod
    def _crear_notif_confirmada(llamada: Llamada):
        med_nombre = (
            llamada.medicamento.nombre if llamada.medicamento else "medicamento"
        )
        NotificacionService.crear_notificacion_llamada(
            usuario=llamada.usuario,
            titulo=f"Toma confirmada — {med_nombre}",
            mensaje=f"{llamada.paciente.nombre} confirmó haber tomado {med_nombre}.",
            paciente=llamada.paciente,
            medicamento=llamada.medicamento,
        )
        # Enviar email de toma confirmada
        EmailService.enviar_email_toma_confirmada(
            usuario=llamada.usuario,
            paciente_nombre=llamada.paciente.nombre,
            medicamento_nombre=med_nombre,
        )

    @staticmethod
    def _crear_alerta_escalada(llamada: Llamada):
        med_nombre = (
            llamada.medicamento.nombre if llamada.medicamento else "medicamento"
        )
        NotificacionService.crear_notificacion_alerta(
            usuario=llamada.usuario,
            titulo=f"Sin respuesta tras {llamada.intentos} intento(s) — {med_nombre}",
            mensaje=(
                f"{llamada.paciente.nombre} no ha confirmado la toma de {med_nombre} "
                f"después de {llamada.intentos} intento(s). Se requiere atención manual."
            ),
            paciente=llamada.paciente,
            medicamento=llamada.medicamento,
        )

    @staticmethod
    def _crear_alerta_no_tomo(llamada: Llamada, palabras_paciente: str = ""):
        med_nombre = (
            llamada.medicamento.nombre if llamada.medicamento else "medicamento"
        )
        detalle = f' El paciente dijo: "{palabras_paciente}".' if palabras_paciente else ""
        NotificacionService.crear_notificacion_alerta(
            usuario=llamada.usuario,
            titulo=f"Medicamento no tomado — {med_nombre}",
            mensaje=(
                f"{llamada.paciente.nombre} reportó que no tomó {med_nombre} "
                f"durante la llamada de recordatorio.{detalle}"
            ),
            paciente=llamada.paciente,
            medicamento=llamada.medicamento,
        )
        # Enviar email de toma no confirmada
        EmailService.enviar_email_toma_no_confirmada(
            usuario=llamada.usuario,
            paciente_nombre=llamada.paciente.nombre,
            medicamento_nombre=med_nombre,
        )

    @staticmethod
    def _crear_alerta_despues(llamada: Llamada, palabras_paciente: str = ""):
        med_nombre = (
            llamada.medicamento.nombre if llamada.medicamento else "medicamento"
        )
        detalle = f' El paciente dijo: "{palabras_paciente}".' if palabras_paciente else ""
        NotificacionService.crear_notificacion_alerta(
            usuario=llamada.usuario,
            titulo=f"Paciente pospuso toma — {med_nombre}",
            mensaje=(
                f"{llamada.paciente.nombre} indicó que tomará {med_nombre} más tarde.{detalle} "
                f"Se programó un reintento automático."
            ),
            paciente=llamada.paciente,
            medicamento=llamada.medicamento,
        )
        # Enviar email de toma aplazada
        EmailService.enviar_email_toma_aplazada(
            usuario=llamada.usuario,
            paciente_nombre=llamada.paciente.nombre,
            medicamento_nombre=med_nombre,
        )

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
        # Enviar email de llamada no atendida
        EmailService.enviar_email_llamada_no_atendida(
            usuario=llamada.usuario,
            paciente_nombre=llamada.paciente.nombre,
            medicamento_nombre=med_nombre,
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
