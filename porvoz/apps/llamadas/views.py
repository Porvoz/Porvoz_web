import logging
import re as _re
import unicodedata

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.llamadas.models import Llamada, RespuestaLlamada
from apps.llamadas.services.llamada_service import LlamadaService
from apps.llamadas.services.proveedor_voz_service import ProveedorVozService
from apps.shared.decorators import verify_twilio_signature, deduplicate_webhook, rate_limit_by_key
from apps.medicamentos.models import Medicamento
from apps.pacientes.models import Paciente

logger = logging.getLogger(__name__)

# TTL para conversaciones activas en cache (10 minutos — una llamada no dura más)
_CONV_TTL = 600
MAX_TURNOS = 3           # máximo intercambios con Gemini (solo para respuestas ambiguas)
MAX_HISTORIAL_LINEAS = 4  # líneas de historial enviadas a Gemini


def _conv_key(call_sid: str) -> str:
    return f"conv:{call_sid}"


def _get_conv(call_sid: str) -> dict:
    return cache.get(_conv_key(call_sid)) or {}


def _set_conv(call_sid: str, data: dict):
    cache.set(_conv_key(call_sid), data, _CONV_TTL)


def _del_conv(call_sid: str):
    cache.delete(_conv_key(call_sid))

# Palabras clave para detectar la intención del paciente en su respuesta
_FRASES_NEGATIVAS = [
    "no lo tomé", "no lo tome", "no tome", "no tomé",
    "no he tomado", "no pude", "no pude tomarlo",
    "todavia no", "todavía no", "aun no", "aún no",
    "olvide", "olvidé", "se me olvido", "se me olvidó",
    "no lo tengo", "no tengo el medicamento",
    "no lo he tomado", "aun no lo he tomado",
    "no me lo he tomado", "no me lo tomé",
    "no", "nope", "negativo",
]
_FRASES_POSITIVAS = [
    # Con tilde y sin tilde (Twilio STT varía)
    "si lo tome", "sí lo tomé", "si lo tomé", "sí lo tome",
    "ya lo tome", "ya lo tomé",
    "lo tome", "lo tomé",
    "ya tome", "ya tomé",
    "tome el medicamento", "tomé el medicamento",
    "lo acabo de tomar", "acabo de tomarlo",
    "me lo tome", "me lo tomé",
    "si señor", "sí señor", "si señora", "sí señora",
    "si claro", "sí claro",
    "si ya", "sí ya",
    "ya me lo tome", "ya me lo tomé",
    "si",   # sin tilde — Twilio STT frecuentemente omite tildes
    "sí",   # con tilde
    "claro", "correcto", "asi es", "así es",
    "por supuesto", "efectivamente",
    "listo", "ok", "bueno", "confirmado",
]
_FRASES_DESPUES = [
    "después", "despues", "luego", "más tarde", "mas tarde",
    "ahorita", "ahora no", "en un momento", "un momento",
    "espere", "espera", "dame un momento", "dame un rato",
    "más tarde lo tomo", "lo tomo después", "lo tomo luego",
    "después lo tomo", "luego lo tomo", "no ahora", "ahora no puedo",
    "ya lo voy a tomar", "voy a tomarlo",
]

# Síntomas graves o señales de emergencia. Si aparecen, cerramos la llamada
# inmediatamente con un mensaje seguro y disparamos alerta CRÍTICA al cuidador.
# NUNCA dejamos que Gemini responda a estos casos — un asistente de voz no
# puede dar consejo médico ni minimizar síntomas.
_FRASES_EMERGENCIA = [
    "no puedo respirar", "no respiro", "me ahogo",
    "dolor en el pecho", "dolor de pecho", "me duele el pecho",
    "infarto", "ataque al corazon", "ataque al corazón",
    "derrame", "no me puedo mover", "no siento",
    "me caí", "me cai", "me desmayé", "me desmaye",
    "estoy sangrando", "sangro mucho",
    "convulsion", "convulsión", "estoy convulsionando",
    "ayuda", "auxilio", "emergencia", "ambulancia",
    "me siento muy mal", "me estoy muriendo", "me muero",
    "ya no aguanto", "no aguanto el dolor",
]

# Rechazo explícito del tratamiento — distinto a "no lo tomé hoy".
# Indica que el paciente no quiere seguir con el medicamento.
_FRASES_RECHAZO = [
    "no quiero tomarlo nunca", "no lo voy a tomar mas", "no lo voy a tomar más",
    "no quiero seguir tomandolo", "no quiero seguir tomándolo",
    "ya no lo voy a tomar", "ya no lo tomo",
    "no quiero ese medicamento", "no me sirve",
    "deje de tomarlo", "dejé de tomarlo",
    "no quiero el tratamiento", "rechazo el tratamiento",
]


def _normalizar(texto: str) -> str:
    """
    Quita tildes, pasa a minúsculas y colapsa espacios.
    Twilio STT es inconsistente con los acentos ('si'/'sí', 'tome'/'tomé').
    Normalizamos antes de hacer matching de keywords.
    """
    if not texto:
        return ""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
    return _re.sub(r"\s+", " ", sin_tildes.lower()).strip()


def _contiene_frase(texto_norm: str, frases: list) -> bool:
    """
    Verifica si el texto contiene alguna de las frases.
    Se asume que `texto_norm` y las frases ya pasaron por _normalizar().
    - Frases de 1 palabra: word-boundary match (evita falsos positivos con substrings).
    - Frases de 2+ palabras: substring match (más flexible).
    """
    for frase in frases:
        if " " in frase:
            if frase in texto_norm:
                return True
        else:
            if _re.search(rf"\b{_re.escape(frase)}\b", texto_norm):
                return True
    return False


# Pre-normalizar las listas una sola vez (al importar el módulo)
_FRASES_NEGATIVAS_N  = [_normalizar(f) for f in _FRASES_NEGATIVAS]
_FRASES_POSITIVAS_N  = [_normalizar(f) for f in _FRASES_POSITIVAS]
_FRASES_DESPUES_N    = [_normalizar(f) for f in _FRASES_DESPUES]
_FRASES_EMERGENCIA_N = [_normalizar(f) for f in _FRASES_EMERGENCIA]
_FRASES_RECHAZO_N    = [_normalizar(f) for f in _FRASES_RECHAZO]


def _detectar_resultado(speech: str) -> str | None:
    """
    Analiza el texto del paciente y retorna la intención detectada o None si es ambigua.
    Prioridad: emergencia > rechazo > negativa > positiva > después > None.
    Las dos primeras se evalúan ANTES que cualquier otra: nunca se debe
    minimizar un síntoma grave o un rechazo explícito.
    """
    texto = _normalizar(speech)
    if not texto:
        return None

    # Prioridad máxima — seguridad del paciente
    if _contiene_frase(texto, _FRASES_EMERGENCIA_N):
        return RespuestaLlamada.RESULTADO_EMERGENCIA

    if _contiene_frase(texto, _FRASES_RECHAZO_N):
        return RespuestaLlamada.RESULTADO_RECHAZO

    # Negativa tiene prioridad sobre positiva/después
    if _contiene_frase(texto, _FRASES_NEGATIVAS_N):
        return RespuestaLlamada.RESULTADO_NEGATIVA

    # "ahora" sin indicar toma inmediata → "despues"
    frases_toma_inmediata = (
        "ya lo tome", "lo acabo de tomar", "ya tome", "si lo tome",
    )
    if "ahora" in texto and not any(f in texto for f in frases_toma_inmediata):
        return RespuestaLlamada.RESULTADO_DESPUES

    # Positiva
    if _contiene_frase(texto, _FRASES_POSITIVAS_N):
        return RespuestaLlamada.RESULTADO_CONFIRMADA

    # Después
    if _contiene_frase(texto, _FRASES_DESPUES_N):
        return RespuestaLlamada.RESULTADO_DESPUES

    return None


def _append_asistente(historial: str, mensaje: str) -> str:
    if not mensaje:
        return historial
    if not historial:
        return f"Asistente: {mensaje}"
    return f"{historial}\nAsistente: {mensaje}"


def _safe_registrar_respuesta(call_sid, transcripcion, como_respondio, resultado=None, palabras_paciente=""):
    """
    Wrapper defensivo para LlamadaService.registrar_respuesta: si la BD falla
    (timeout, conexión, integridad), solo loggea y retorna None — un webhook
    NUNCA debe devolver 5xx a Twilio porque dispara reintentos en cascada.
    """
    try:
        return LlamadaService.registrar_respuesta(
            call_sid=call_sid,
            transcripcion=transcripcion,
            como_respondio=como_respondio,
            resultado=resultado,
            palabras_paciente=palabras_paciente,
        )
    except Exception as exc:
        logger.error(
            f"[webhook] Falló registrar_respuesta CallSID={call_sid} "
            f"como_respondio={como_respondio} resultado={resultado}: {exc}",
            exc_info=True,
        )
        return None


def _safe_registrar_estado_final(call_sid, estado_twilio, duracion=None):
    """Wrapper defensivo para LlamadaService.registrar_estado_final."""
    try:
        return LlamadaService.registrar_estado_final(call_sid, estado_twilio, duracion)
    except Exception as exc:
        logger.error(
            f"[webhook_status] Falló registrar_estado_final CallSID={call_sid} "
            f"estado={estado_twilio}: {exc}",
            exc_info=True,
        )
        return None


@login_required
def historial_llamadas(request):
    """Historial global de llamadas del usuario."""
    from django.utils import timezone
    from datetime import timedelta

    qs = (
        Llamada.objects.filter(usuario=request.user)
        .select_related("paciente", "medicamento")
        .prefetch_related("respuesta")
        .order_by("-fecha_programada")
    )

    estado = request.GET.get("estado", "")
    paciente_id = request.GET.get("paciente", "")
    medicamento_id = request.GET.get("medicamento", "")
    fecha_desde = request.GET.get("fecha_desde", "")
    fecha_hasta = request.GET.get("fecha_hasta", "")

    if estado:
        qs = qs.filter(estado=estado)
    if paciente_id:
        qs = qs.filter(paciente_id=paciente_id)
    if medicamento_id:
        qs = qs.filter(medicamento_id=medicamento_id)
    if fecha_desde:
        qs = qs.filter(fecha_programada__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_programada__date__lte=fecha_hasta)

    pacientes = Paciente.objects.filter(usuario=request.user, activo=True).order_by("nombre")
    medicamentos = Medicamento.objects.filter(
        paciente__usuario=request.user, activo=True
    ).select_related("paciente").order_by("paciente__nombre", "nombre")

    hay_filtros = any([estado, paciente_id, medicamento_id, fecha_desde, fecha_hasta])

    # Estadísticas generales (sin filtros)
    ahora = timezone.now()
    hace_7_dias = ahora - timedelta(days=7)

    total_llamadas = Llamada.objects.filter(usuario=request.user).count()
    llamadas_semana = Llamada.objects.filter(
        usuario=request.user,
        fecha_programada__gte=hace_7_dias,
        estado__in=[Llamada.ESTADO_COMPLETADA, Llamada.ESTADO_FALLIDA],
    ).count()
    atendidas_semana = Llamada.objects.filter(
        usuario=request.user,
        fecha_programada__gte=hace_7_dias,
        respuesta__como_respondio=RespuestaLlamada.RESPUESTA_ATENDIDA,
    ).count()
    sin_respuesta = Llamada.objects.filter(
        usuario=request.user,
        respuesta__como_respondio__in=[
            RespuestaLlamada.RESPUESTA_NO_ATENDIDA,
            RespuestaLlamada.RESPUESTA_BUZON,
        ],
    ).count()
    adherencia = round((atendidas_semana / llamadas_semana * 100) if llamadas_semana > 0 else 0)

    return render(
        request,
        "llamadas/historial.html",
        {
            "llamadas": qs,
            "pacientes": pacientes,
            "medicamentos": medicamentos,
            "estado_filtro": estado,
            "paciente_filtro": paciente_id,
            "medicamento_filtro": medicamento_id,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "estados": Llamada.ESTADO_CHOICES,
            "total": qs.count(),
            "hay_filtros": hay_filtros,
            "total_llamadas": total_llamadas,
            "llamadas_semana": llamadas_semana,
            "atendidas_semana": atendidas_semana,
            "sin_respuesta": sin_respuesta,
            "adherencia": adherencia,
        },
    )


# ------------------------------------------------------------------
# Webhooks Twilio (sin CSRF — Twilio no envía token)
# ------------------------------------------------------------------


@csrf_exempt
@require_http_methods(["POST"])
@verify_twilio_signature
@rate_limit_by_key(key_func=lambda r: r.POST.get("CallSid", "unknown"), rate="10/s")
@deduplicate_webhook(
    key_func=lambda r: f"voice:{r.POST.get('CallSid', '')}",
    ttl=600,
)
def webhook_voice(request):
    """
    Inicio de llamada. Saludo completamente estático — sin llamada a Gemini.

    Maneja machine_detection de Twilio: si detecta buzón de voz, cierra
    inmediatamente y registra la llamada como 'buzon'.
    """
    nombre_med      = request.GET.get("nombre_med", "su medicamento")
    instrucciones   = request.GET.get("instrucciones", "")
    nombre_paciente = request.GET.get("nombre_paciente", "")
    call_sid        = request.POST.get("CallSid", "")

    logger.info(f"[webhook_voice] Inicio de llamada CallSID={call_sid} Medicamento={nombre_med}")

    # Saludo natural — incluye las instrucciones del medicamento si existen,
    # para que el paciente escuche el contexto que el cuidador configuró.
    saludo_inicio = f"Hola{' ' + nombre_paciente if nombre_paciente else ''}, le llama Porvoz."
    instrucciones_limpias = (instrucciones or "").strip()
    if instrucciones_limpias:
        # Asegura punto final para que el TTS pause antes de la pregunta.
        if instrucciones_limpias[-1] not in ".!?":
            instrucciones_limpias += "."
        saludo = f"{saludo_inicio} Es hora de tomar su {nombre_med}. {instrucciones_limpias} ¿Ya lo tomó?"
    else:
        saludo = f"{saludo_inicio} Es hora de tomar su {nombre_med}. ¿Ya lo tomó?"

    # Detectar buzón de voz — evitar falsos positivos con machine_start.
    answered_by = request.POST.get("AnsweredBy", "")
    if answered_by in ("machine_end_beep", "machine_end_silence", "fax"):
        if call_sid:
            transcripcion_buzon = _append_asistente(
                f"Asistente: {saludo}", ProveedorVozService.MSG_TIMEOUT
            )
            _safe_registrar_respuesta(
                call_sid, transcripcion_buzon, RespuestaLlamada.RESPUESTA_BUZON
            )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_TIMEOUT),
            content_type="text/xml",
        )

    if call_sid:
        _set_conv(call_sid, {
            "history": f"Asistente: {saludo}",
            "nombre_med": nombre_med,
            "instrucciones": instrucciones,
            "nombre_paciente": nombre_paciente,
            "resultado": None,
            "turnos": 0,
        })

    import urllib.parse as _urlp
    base_url   = ProveedorVozService.get_base_url()
    gather_url = (
        f"{base_url}/llamadas/webhook/gather/"
        f"?nombre_med={_urlp.quote(nombre_med)}"
        f"&instrucciones={_urlp.quote(instrucciones)}"
        f"&nombre_paciente={_urlp.quote(nombre_paciente)}"
    )
    return HttpResponse(
        ProveedorVozService.build_twiml_gather(saludo, gather_url),
        content_type="text/xml",
    )


@csrf_exempt
@require_http_methods(["POST"])
@verify_twilio_signature
@rate_limit_by_key(key_func=lambda r: r.POST.get("CallSid", "unknown"), rate="10/s")
@deduplicate_webhook(
    key_func=lambda r: f"gather:{r.POST.get('CallSid', '')}:{(r.POST.get('SpeechResult', '') or '').strip()}",
    ttl=120,
)
def webhook_gather(request):
    """Recibe lo que dijo el paciente y responde con IA."""
    call_sid = request.POST.get("CallSid", "")
    speech   = request.POST.get("SpeechResult", "").strip()

    sesion = _get_conv(call_sid) or {
        "history": "",
        "nombre_med": request.GET.get("nombre_med", "medicamento"),
        "instrucciones": request.GET.get("instrucciones", ""),
        "nombre_paciente": request.GET.get("nombre_paciente", ""),
        "turnos": 0,
        "resultado": None,
    }
    historial        = sesion.get("history", "")
    nombre_med       = sesion.get("nombre_med", "medicamento")
    instrucciones    = sesion.get("instrucciones", "")
    nombre_paciente  = sesion.get("nombre_paciente", "")
    turnos           = sesion.get("turnos", 0) + 1
    resultado_sesion = sesion.get("resultado", None)

    # ------------------------------------------------------------------ #
    # 0. Paciente no habló — colgar educadamente sin Gemini               #
    # ------------------------------------------------------------------ #
    if not speech:
        _del_conv(call_sid)
        transcripcion_final = _append_asistente(
            historial, ProveedorVozService.MSG_NO_ESCUCHO
        )
        _safe_registrar_respuesta(
            call_sid, transcripcion_final,
            RespuestaLlamada.RESPUESTA_ATENDIDA, RespuestaLlamada.RESULTADO_SIN_CONFIRMAR,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_NO_ESCUCHO),
            content_type="text/xml",
        )

    historial_actualizado = (
        f"{historial}\nUsuario: {speech}" if historial else f"Usuario: {speech}"
    )

    # Persistir transcripción parcial turno a turno — si la sesión se pierde
    # (ngrok caído, timeout de Twilio), al menos queda registrada en la BD.
    # Cualquier cierre posterior (determinista o por Gemini) la sobreescribe.
    if call_sid:
        try:
            LlamadaService.actualizar_transcripcion_parcial(call_sid, historial_actualizado)
        except Exception as e:
            logger.warning(f"[webhook_gather] No se pudo persistir transcripción parcial: {e}")

    # ------------------------------------------------------------------ #
    # 1. Detectar intención en el texto del paciente                       #
    # ------------------------------------------------------------------ #
    resultado_turno = _detectar_resultado(speech)
    logger.info(f"[webhook_gather] CallSID={call_sid} Turno={turnos} STT='{speech}' Detectado={resultado_turno} ResultadoSesion={resultado_sesion}")
    if resultado_turno and resultado_sesion is None:
        resultado_sesion = resultado_turno

    # ------------------------------------------------------------------ #
    # 2a. EMERGENCIA — máxima prioridad, cierre inmediato y seguro        #
    # ------------------------------------------------------------------ #
    if resultado_sesion == RespuestaLlamada.RESULTADO_EMERGENCIA:
        _del_conv(call_sid)
        transcripcion_final = _append_asistente(
            historial_actualizado, ProveedorVozService.MSG_EMERGENCIA
        )
        _safe_registrar_respuesta(
            call_sid, transcripcion_final,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
            palabras_paciente=speech,
        )
        logger.warning(
            f"[webhook_gather] EMERGENCIA detectada CallSID={call_sid} "
            f"speech='{speech[:120]}'"
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_EMERGENCIA),
            content_type="text/xml",
        )

    # ------------------------------------------------------------------ #
    # 2b. RECHAZO de tratamiento — cierre inmediato + alerta crítica      #
    # ------------------------------------------------------------------ #
    if resultado_sesion == RespuestaLlamada.RESULTADO_RECHAZO:
        _del_conv(call_sid)
        transcripcion_final = _append_asistente(
            historial_actualizado, ProveedorVozService.MSG_RECHAZO
        )
        _safe_registrar_respuesta(
            call_sid, transcripcion_final,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
            palabras_paciente=speech,
        )
        logger.warning(
            f"[webhook_gather] RECHAZO de tratamiento CallSID={call_sid} "
            f"speech='{speech[:120]}'"
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_RECHAZO),
            content_type="text/xml",
        )

    # ------------------------------------------------------------------ #
    # 2. Cierre determinista — sin Gemini — cuando la intención es clara  #
    # ------------------------------------------------------------------ #
    if resultado_sesion == RespuestaLlamada.RESULTADO_CONFIRMADA:
        _del_conv(call_sid)
        transcripcion_final = _append_asistente(
            historial_actualizado, ProveedorVozService.MSG_CONFIRMADO
        )
        _safe_registrar_respuesta(
            call_sid, transcripcion_final,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_CONFIRMADO),
            content_type="text/xml",
        )

    if resultado_sesion == RespuestaLlamada.RESULTADO_NEGATIVA:
        _del_conv(call_sid)
        transcripcion_final = _append_asistente(
            historial_actualizado, ProveedorVozService.MSG_NEGATIVO
        )
        _safe_registrar_respuesta(
            call_sid, transcripcion_final,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_NEGATIVO),
            content_type="text/xml",
        )

    if resultado_sesion == RespuestaLlamada.RESULTADO_DESPUES:
        _del_conv(call_sid)
        transcripcion_final = _append_asistente(
            historial_actualizado, ProveedorVozService.MSG_DESPUES
        )
        _safe_registrar_respuesta(
            call_sid, transcripcion_final,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
            palabras_paciente=speech,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_DESPUES),
            content_type="text/xml",
        )

    # ------------------------------------------------------------------ #
    # 3. Límite de turnos — forzar cierre sin más Gemini                  #
    # ------------------------------------------------------------------ #
    if turnos > MAX_TURNOS:
        _del_conv(call_sid)
        transcripcion_final = _append_asistente(
            historial_actualizado, ProveedorVozService.MSG_TIMEOUT
        )
        # Intenta detectar resultado una última vez si aún está sin confirmar
        if resultado_sesion is None:
            resultado_final = _detectar_resultado(historial_actualizado)
            resultado_sesion = resultado_final or RespuestaLlamada.RESULTADO_SIN_CONFIRMAR
        logger.info(f"[webhook_gather] Cierre por MAX_TURNOS CallSID={call_sid} ResultadoFinal={resultado_sesion}")
        _safe_registrar_respuesta(
            call_sid, transcripcion_final,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_TIMEOUT),
            content_type="text/xml",
        )

    # ------------------------------------------------------------------ #
    # 4. Solo aquí se llama a Gemini (respuesta ambigua, dentro del límite) #
    # ------------------------------------------------------------------ #
    lineas             = historial_actualizado.split("\n")
    historial_reducido = "\n".join(lineas[-MAX_HISTORIAL_LINEAS:])

    logger.info(f"[webhook_gather] CallSID={call_sid} Turno={turnos} Resultado={resultado_sesion} → Llamando a Gemini")
    try:
        respuesta_ia = ProveedorVozService.generar_respuesta_ia(
            speech, nombre_med, instrucciones, nombre_paciente, historial_reducido
        )
        logger.info(f"[webhook_gather] Gemini respondió: {respuesta_ia[:50]}")
    except Exception as e:
        logger.error(f"[webhook_gather] EXCEPCIÓN en Gemini: {type(e).__name__}: {e}", exc_info=True)
        _del_conv(call_sid)
        transcripcion_final = _append_asistente(
            historial_actualizado, ProveedorVozService.MSG_TIMEOUT
        )
        # Intenta detectar resultado si aún no se ha confirmado nada
        if resultado_sesion is None:
            resultado_final = _detectar_resultado(historial_actualizado)
            resultado_sesion = resultado_final or RespuestaLlamada.RESULTADO_SIN_CONFIRMAR
        logger.info(f"[webhook_gather] Cierre por error Gemini CallSID={call_sid} ResultadoFinal={resultado_sesion}")
        _safe_registrar_respuesta(
            call_sid, transcripcion_final,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_TIMEOUT),
            content_type="text/xml",
        )

    nuevo_historial = f"{historial_actualizado}\nAsistente: {respuesta_ia}"
    _set_conv(call_sid, {
        **sesion,
        "history": nuevo_historial,
        "turnos": turnos,
        "resultado": resultado_sesion,
    })

    # Si Gemini incluyó despedida, cerrar aquí
    _DESPEDIDAS = ("hasta luego", "adiós", "adios", "que tenga", "cuídese", "buen día", "buen dia")
    if any(d in respuesta_ia.lower() for d in _DESPEDIDAS):
        _del_conv(call_sid)
        # Intenta detectar resultado una última vez si aún está sin confirmar
        if resultado_sesion is None:
            resultado_final = _detectar_resultado(nuevo_historial)
            resultado_sesion = resultado_final or RespuestaLlamada.RESULTADO_SIN_CONFIRMAR
        logger.info(f"[webhook_gather] Cierre por despedida de Gemini CallSID={call_sid} ResultadoFinal={resultado_sesion}")
        _safe_registrar_respuesta(
            call_sid, nuevo_historial,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(respuesta_ia), content_type="text/xml"
        )

    base_url   = ProveedorVozService.get_base_url()
    gather_url = f"{base_url}/llamadas/webhook/gather/"
    return HttpResponse(
        ProveedorVozService.build_twiml_continuar(respuesta_ia, gather_url),
        content_type="text/xml",
    )


# Estados finales de Twilio que realmente representan un cierre de llamada.
# Intermedios (initiated, ringing, in-progress) se ignoran.
_ESTADOS_TERMINALES = {"completed", "busy", "no-answer", "failed", "canceled"}


@csrf_exempt
@require_http_methods(["POST"])
@verify_twilio_signature
@rate_limit_by_key(key_func=lambda r: r.POST.get("CallSid", "unknown"), rate="10/s")
@deduplicate_webhook(
    key_func=lambda r: f"{r.POST.get('CallSid', '')}:{r.POST.get('CallStatus', '')}",
    ttl=600,
)
def webhook_status(request):
    """
    Twilio notifica el estado de la llamada. Solo procesamos estados terminales
    (completed, busy, no-answer, failed, canceled). Deduplicación por
    CallSid+CallStatus para tolerar reintentos de Twilio sin bloquear cambios
    legítimos de estado.
    """
    call_sid     = request.POST.get("CallSid", "")
    call_status  = request.POST.get("CallStatus", "")
    call_duration = request.POST.get("CallDuration", "0")

    if not call_sid:
        return HttpResponse(status=200)

    # Ignorar estados intermedios — son ruido
    if call_status not in _ESTADOS_TERMINALES:
        logger.info(
            f"[webhook_status] Ignorando estado no terminal CallSID={call_sid} CallStatus={call_status}"
        )
        return HttpResponse(status=200)

    try:
        duracion = int(call_duration)
    except (ValueError, TypeError):
        duracion = None

    historial = _get_conv(call_sid).get("history", "")
    _safe_registrar_estado_final(call_sid, call_status, duracion)
    # No borramos la conversación aquí: Twilio puede enviar el status antes del gather.
    # El TTL de cache la limpia sola y así mantenemos la transcripción completa.

    try:
        ya_hay_respuesta = RespuestaLlamada.objects.filter(
            llamada__call_sid=call_sid
        ).exists()
    except Exception as exc:
        logger.error(f"[webhook_status] Falló consulta RespuestaLlamada CallSID={call_sid}: {exc}")
        return HttpResponse(status=200)

    if call_status in ("no-answer", "busy", "failed", "canceled"):
        # Solo registrar como no_atendida si NO hay respuesta ya grabada — evita
        # pisar una confirmación que llegó por webhook_gather.
        if not ya_hay_respuesta:
            _safe_registrar_respuesta(
                call_sid, historial, RespuestaLlamada.RESPUESTA_NO_ATENDIDA
            )
    elif call_status == "completed" and not ya_hay_respuesta:
        # Cuelgue antes del primer gather: si la duración fue muy corta y no
        # tenemos historial de conversación, marcarlo como no_atendida es más
        # honesto que sin_confirmar (el paciente no llegó a interactuar).
        if not historial or (duracion is not None and duracion < 5):
            _safe_registrar_respuesta(
                call_sid, historial, RespuestaLlamada.RESPUESTA_NO_ATENDIDA
            )
        else:
            _safe_registrar_respuesta(
                call_sid,
                historial,
                RespuestaLlamada.RESPUESTA_ATENDIDA,
                RespuestaLlamada.RESULTADO_SIN_CONFIRMAR,
            )

    return HttpResponse(status=200)


@login_required
@require_http_methods(["POST"])
def cancelar_llamada(request, llamada_id: int):
    """Cancela una llamada programada. Solo aplica a estado 'programada'."""
    from django.contrib import messages
    from django.shortcuts import get_object_or_404, redirect

    llamada = get_object_or_404(Llamada, id=llamada_id, usuario=request.user)
    if llamada.estado == Llamada.ESTADO_PROGRAMADA:
        llamada.estado = Llamada.ESTADO_FALLIDA
        llamada.save(update_fields=["estado"])
        messages.success(request, "Llamada cancelada.")
    else:
        messages.error(request, "Solo se pueden cancelar llamadas con estado 'Programada'.")

    # Volver al historial manteniendo el filtro de paciente si venía de allí
    next_url = request.POST.get("next", "")
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect("historial_llamadas")
