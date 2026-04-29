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
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from apps.llamadas.models import AuditoriaLog, Llamada, RespuestaLlamada
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

        Returns:
            Lista de Llamadas creadas
        """
        # Cancelar llamadas programadas anteriores de este medicamento
        Llamada.objects.filter(
            medicamento=medicamento,
            estado=Llamada.ESTADO_PROGRAMADA,
        ).delete()

        ahora = timezone.now()
        paciente = medicamento.paciente

        # Usar timezone del paciente (default America/Bogota)
        try:
            tz_paciente = ZoneInfo(paciente.timezone or "America/Bogota")
        except ZoneInfoNotFoundError:
            tz_paciente = ZoneInfo("America/Bogota")

        hoy = ahora.astimezone(tz_paciente).date()
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
                # Construir datetime en timezone del paciente y convertir a UTC
                dt_toma_hoy = datetime.combine(hoy, hora).replace(tzinfo=tz_paciente)
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
                    paciente=paciente,
                    fecha_programada=fecha,
                )
                creadas.append(llamada)

        elif medicamento.frecuencia_tipo == medicamento.FRECUENCIA_CADA_X_HORAS:
            hora_inicio = LlamadaService._as_time(medicamento.hora_inicio)
            if hora_inicio and medicamento.cada_x_horas:
                dt_base = datetime.combine(hoy, hora_inicio).replace(tzinfo=tz_paciente)
                intervalo = timedelta(hours=medicamento.cada_x_horas)
                # Siguiente dosis que aún no haya pasado
                dt_siguiente = dt_base
                while dt_siguiente - offset <= ahora:
                    dt_siguiente += intervalo

                llamada = LlamadaService.crear_llamada_programada(
                    medicamento=medicamento,
                    usuario=usuario,
                    paciente=paciente,
                    fecha_programada=dt_siguiente - offset,
                )
                creadas.append(llamada)

        return creadas

    @staticmethod
    def limpiar_llamadas_vencidas():
        """
        Marca como fallida toda Llamada con estado en_curso y fecha_ejecutada
        anterior a hace 10 minutos. Evita acumulación de llamadas fantasma cuando
        el webhook de status no llega (ej: ngrok caído).
        """
        corte = timezone.now() - timedelta(minutes=10)
        vencidas = Llamada.objects.filter(
            estado=Llamada.ESTADO_EN_CURSO,
            fecha_ejecutada__lt=corte,
        )
        count = vencidas.count()
        if count:
            vencidas.update(estado=Llamada.ESTADO_FALLIDA)
            logger.info(f"[LlamadaService] {count} llamada(s) en_curso vencidas → fallida.")
        return count

    @staticmethod
    def ejecutar_llamadas_pendientes(max_workers=5):
        """
        Busca llamadas programadas con fecha vencida y las ejecuta EN PARALELO.
        Usa ThreadPoolExecutor para disparar múltiples llamadas simultáneamente.

        Antes de despachar:
          - Limpia llamadas zombi atascadas en EN_CURSO (housekeeping).
          - Cancela llamadas cuyo paciente o medicamento ya no estén activos.

        Args:
            max_workers: Máximo de llamadas paralelas (default 5)
        """
        from apps.llamadas.services.proveedor_voz_service import ProveedorVozService

        # Housekeeping: cierra llamadas que quedaron colgadas en EN_CURSO
        # (típicamente porque el webhook de status nunca llegó).
        LlamadaService.limpiar_llamadas_vencidas()

        ahora = timezone.now()
        candidatas = Llamada.objects.filter(
            estado=Llamada.ESTADO_PROGRAMADA,
            fecha_programada__lte=ahora,
        ).select_related("medicamento", "paciente", "usuario")

        # Cancelar las que apunten a paciente o medicamento inactivos.
        # Si el cuidador desactivó el medicamento o eliminó al paciente entre
        # programación y ejecución, no debemos llamar — marcamos como fallida.
        canceladas = candidatas.filter(
            models.Q(paciente__activo=False)
            | models.Q(medicamento__isnull=True)
            | models.Q(medicamento__activo=False)
        )
        n_canceladas = canceladas.count()
        if n_canceladas:
            canceladas.update(estado=Llamada.ESTADO_FALLIDA)
            logger.info(
                f"[LlamadaService] {n_canceladas} llamada(s) canceladas: "
                f"paciente o medicamento inactivo."
            )

        pendientes = list(
            candidatas.filter(
                paciente__activo=True,
                medicamento__activo=True,
            )
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

        Claim atómico: solo una instancia del scheduler puede pasar del PROGRAMADA→EN_CURSO.
        Si otro proceso (u otro thread) ya claimó la llamada, salimos silenciosamente.
        """
        from apps.llamadas.services.proveedor_voz_service import ProveedorVozService

        ahora = timezone.now()
        claimed = Llamada.objects.filter(
            pk=llamada.pk,
            estado=Llamada.ESTADO_PROGRAMADA,
        ).update(estado=Llamada.ESTADO_EN_CURSO, fecha_ejecutada=ahora)

        if claimed == 0:
            logger.info(
                f"[LlamadaService] Llamada #{llamada.pk} ya fue claimada por otro proceso; saltando."
            )
            return

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
            # Validar número antes de llamar a Twilio
            from apps.shared.services.telefono_service import TelefonoService
            if not TelefonoService.es_numero_valido(numero):
                error_msg = f"Número de teléfono inválido: {numero}"
                logger.warning(f"[LlamadaService] Llamada #{llamada.id}: {error_msg}")
                llamada.estado = Llamada.ESTADO_FALLIDA
                llamada.save(update_fields=["estado"])
                LlamadaService._crear_alerta_fallo(llamada, error_msg)
                return

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
                voice_url=voice_url,
                status_url=status_url,
            )

            # El estado EN_CURSO + fecha_ejecutada ya fueron seteados en el claim atómico arriba.
            llamada.call_sid = call_sid
            llamada.save(update_fields=["call_sid"])

            # Registrar auditoría
            LlamadaService._registrar_auditoria(
                usuario=llamada.usuario,
                obj=llamada,
                accion=AuditoriaLog.ACCION_UPDATE,
                cambios={"estado": ["programada", "en_curso"], "call_sid": call_sid},
            )

        except Exception as e:
            error_msg = str(e)
            # Errores de red transientes de Twilio → reprogramar en 5 min en vez de fallar
            es_error_red = any(kw in error_msg.lower() for kw in (
                "connection", "timeout", "network", "ssl", "socket", "read timed out"
            ))
            if es_error_red and llamada.intentos == 0:
                logger.warning(
                    f"[LlamadaService] Error de red en llamada #{llamada.id}, "
                    f"reprogramando en 5 min: {error_msg}"
                )
                llamada.fecha_programada = timezone.now() + timedelta(minutes=5)
                llamada.intentos = 1
                llamada.save(update_fields=["fecha_programada", "intentos"])
            else:
                logger.error(
                    f"[LlamadaService] Error ejecutando llamada #{llamada.id}: {error_msg}"
                )
                llamada.estado = Llamada.ESTADO_FALLIDA
                llamada.save(update_fields=["estado"])
                LlamadaService._crear_alerta_fallo(llamada, error_msg)

    @staticmethod
    def _registrar_auditoria(usuario, obj, accion: str, cambios: dict = None):
        """Registra auditoría. Si falla, solo registra el error en logs (no interfiere con llamadas)."""
        try:
            content_type = ContentType.objects.get_for_model(obj.__class__)
            AuditoriaLog.objects.create(
                usuario=usuario,
                contenido_type=content_type,
                objeto_id=obj.pk,
                objeto_str=str(obj),
                accion=accion,
                cambios=cambios or {},
            )
        except Exception as exc:
            logger.warning(f"[AuditoriaLog] Fallo al registrar (no crítico): {exc}")

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
            elif resultado_final == RespuestaLlamada.RESULTADO_EMERGENCIA:
                # Crítica: NO se reintenta — un reintento podría ser perjudicial.
                LlamadaService.crear_alerta_emergencia(llamada, palabras_paciente)
            elif resultado_final == RespuestaLlamada.RESULTADO_RECHAZO:
                # Crítica: NO se reintenta — el paciente rechazó explícitamente.
                LlamadaService.crear_alerta_rechazo_tratamiento(llamada, palabras_paciente)

        return respuesta

    @staticmethod
    def actualizar_transcripcion_parcial(call_sid: str, transcripcion: str) -> None:
        """
        Persiste la transcripción parcial de una llamada en curso, turno a turno.
        Upsert sobre RespuestaLlamada con como_respondio='atendida' y resultado='sin_confirmar'.

        Si un webhook final llega después, registrar_respuesta sobreescribirá estos valores.
        Si el webhook final nunca llega (ngrok caído, timeout), al menos queda la transcripción.
        """
        if not call_sid or not transcripcion:
            return
        llamada = Llamada.objects.filter(call_sid=call_sid).first()
        if not llamada:
            return
        RespuestaLlamada.objects.update_or_create(
            llamada=llamada,
            defaults={
                "como_respondio": RespuestaLlamada.RESPUESTA_ATENDIDA,
                "resultado": RespuestaLlamada.RESULTADO_SIN_CONFIRMAR,
                "transcripcion": transcripcion,
            },
        )

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
        nuevo_estado = mapa_estado.get(estado_twilio)
        if nuevo_estado is None:
            logger.info(
                f"[LlamadaService] Ignorando estado no terminal de Twilio para call_sid={call_sid}: {estado_twilio}"
            )
            return

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

        max_reintentos = min(medicamento.max_reintentos, 3)
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
    def _enviar_email_evento(
        *,
        tipo: str,
        llamada: Llamada,
        extra: dict | None = None,
    ) -> None:
        """
        Intenta enviar por Celery; si falla el enqueue, envía en línea como fallback.
        """
        extra = extra or {}

        try:
            from apps.notificaciones.tasks import enviar_email_task

            enviar_email_task.delay(
                tipo=tipo,
                usuario_id=llamada.usuario.id,
                paciente_id=llamada.paciente.id if llamada.paciente else None,
                medicamento_id=llamada.medicamento.id if llamada.medicamento else None,
                extra=extra,
            )
            return
        except Exception as e:
            logger.warning(
                f"[LlamadaService] Falló cola Celery para {tipo}, fallback síncrono: {e}"
            )

        try:
            from apps.notificaciones.services.email_service import EmailService

            handlers = {
                "toma_confirmada": EmailService.enviar_email_toma_confirmada,
                "toma_no_confirmada": EmailService.enviar_email_toma_no_confirmada,
                "toma_aplazada": EmailService.enviar_email_toma_aplazada,
                "llamada_no_atendida": EmailService.enviar_email_llamada_no_atendida,
                "reintentos_agotados": EmailService.enviar_email_reintentos_agotados,
            }

            if tipo in ("emergencia_medica", "rechazo_tratamiento"):
                EmailService.enviar_email_critico_obligatorio(
                    usuario=llamada.usuario,
                    titulo=extra.get("titulo") or "Alerta crítica de Porvoz",
                    mensaje=extra.get("mensaje") or "",
                    paciente=llamada.paciente,
                    medicamento=llamada.medicamento,
                )
                return

            handler = handlers.get(tipo)
            if not handler:
                logger.warning(f"[LlamadaService] Tipo de email no soportado: {tipo}")
                return

            handler(
                usuario=llamada.usuario,
                paciente=llamada.paciente,
                medicamento=llamada.medicamento,
                **extra,
            )
        except Exception as e:
            logger.warning(
                f"[LlamadaService] Fallback síncrono falló para {tipo} (no crítico): {e}"
            )

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
        LlamadaService._enviar_email_evento(tipo="toma_confirmada", llamada=llamada)

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
        LlamadaService._enviar_email_evento(
            tipo="reintentos_agotados",
            llamada=llamada,
            extra={"intentos": llamada.intentos},
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
        LlamadaService._enviar_email_evento(tipo="toma_no_confirmada", llamada=llamada)

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
        LlamadaService._enviar_email_evento(tipo="toma_aplazada", llamada=llamada)

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
        LlamadaService._enviar_email_evento(tipo="llamada_no_atendida", llamada=llamada)

    @staticmethod
    def crear_alerta_emergencia(llamada: Llamada, palabras_paciente: str = ""):
        """
        Alerta CRÍTICA: el paciente reportó síntomas graves durante la llamada.
        El email se envía OBLIGATORIAMENTE, ignorando las preferencias del usuario,
        porque es un evento de seguridad que no puede silenciarse.
        """
        from apps.notificaciones.models import Notificacion

        med_nombre = llamada.medicamento.nombre if llamada.medicamento else "medicamento"
        detalle = f' El paciente dijo: "{palabras_paciente}".' if palabras_paciente else ""
        titulo = f"EMERGENCIA — {llamada.paciente.nombre}"
        mensaje = (
            f"{llamada.paciente.nombre} reportó síntomas que podrían ser graves "
            f"durante la llamada de recordatorio de {med_nombre}.{detalle} "
            f"Contáctelo de inmediato."
        )
        NotificacionService.crear_notificacion_alerta(
            usuario=llamada.usuario,
            titulo=titulo,
            mensaje=mensaje,
            paciente=llamada.paciente,
            medicamento=llamada.medicamento,
            prioridad=Notificacion.PRIORIDAD_CRITICA,
        )
        LlamadaService._enviar_email_evento(
            tipo="emergencia_medica",
            llamada=llamada,
            extra={"titulo": titulo, "mensaje": mensaje},
        )

    @staticmethod
    def crear_alerta_rechazo_tratamiento(llamada: Llamada, palabras_paciente: str = ""):
        """
        Alerta CRÍTICA: el paciente rechaza explícitamente el tratamiento.
        Email obligatorio porque puede implicar discontinuación médica grave.
        """
        from apps.notificaciones.models import Notificacion

        med_nombre = llamada.medicamento.nombre if llamada.medicamento else "medicamento"
        detalle = f' El paciente dijo: "{palabras_paciente}".' if palabras_paciente else ""
        titulo = f"Rechazo de tratamiento — {med_nombre}"
        mensaje = (
            f"{llamada.paciente.nombre} indicó que NO desea continuar con "
            f"{med_nombre}.{detalle} Considere contactar al paciente y a su médico."
        )
        NotificacionService.crear_notificacion_alerta(
            usuario=llamada.usuario,
            titulo=titulo,
            mensaje=mensaje,
            paciente=llamada.paciente,
            medicamento=llamada.medicamento,
            prioridad=Notificacion.PRIORIDAD_CRITICA,
        )
        LlamadaService._enviar_email_evento(
            tipo="rechazo_tratamiento",
            llamada=llamada,
            extra={"titulo": titulo, "mensaje": mensaje},
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
