import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.llamadas.models import Llamada, RespuestaLlamada
from apps.llamadas.services.llamada_service import LlamadaService
from apps.llamadas.services.proveedor_voz_service import ProveedorVozService
from apps.llamadas.decorators import verify_twilio_signature, deduplicate_webhook
from apps.medicamentos.models import Medicamento
from apps.pacientes.models import Paciente

logger = logging.getLogger(__name__)

# Almacén en memoria de conversaciones activas {call_sid: {history, mensaje, turnos, resultado}}
_conversaciones = {}

MAX_TURNOS = 3           # máximo intercambios con Gemini (solo para respuestas ambiguas)
MAX_HISTORIAL_LINEAS = 4  # líneas de historial enviadas a Gemini

# Palabras clave para detectar la intención del paciente en su respuesta
_FRASES_NEGATIVAS = [
    "no lo tomé", "no lo tome", "no tome", "no tomé",
    "no he tomado", "no pude", "no pude tomarlo",
    "todavia no", "todavía no", "aun no", "aún no",
    "olvide", "olvidé", "se me olvido", "se me olvidó",
    "no lo tengo", "no tengo el medicamento",
    "no lo he tomado", "aun no lo he tomado",
    "no me lo he tomado", "no me lo tomé",
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
]
_FRASES_DESPUES = [
    "después", "despues", "luego", "más tarde", "mas tarde",
    "ahorita", "ahora no", "en un momento", "un momento",
    "espere", "espera", "dame un momento", "dame un rato",
    "más tarde lo tomo", "lo tomo después", "lo tomo luego",
    "después lo tomo", "luego lo tomo", "no ahora", "ahora no puedo",
]


def _detectar_resultado(speech: str) -> str | None:
    """
    Analiza el texto del paciente y retorna la intención detectada o None si es ambigua.
    Prioridad: negativa > positiva > después > None.
    """
    texto = speech.lower().strip()
    if not texto:
        return None
    if any(f in texto for f in _FRASES_NEGATIVAS):
        return RespuestaLlamada.RESULTADO_NEGATIVA
    if any(f in texto for f in _FRASES_POSITIVAS):
        return RespuestaLlamada.RESULTADO_CONFIRMADA
    if any(f in texto for f in _FRASES_DESPUES):
        return RespuestaLlamada.RESULTADO_DESPUES
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
def webhook_voice(request):
    """
    Inicio de llamada. Saludo completamente estático — sin llamada a Gemini.

    Maneja machine_detection de Twilio: si detecta buzón de voz, cierra
    inmediatamente y registra la llamada como 'buzon'.
    """
    # Detectar buzón de voz — colgar sin molestar
    answered_by = request.POST.get("AnsweredBy", "")
    if answered_by in ("machine_start", "machine_end_beep", "machine_end_silence", "fax"):
        call_sid = request.POST.get("CallSid", "")
        if call_sid:
            LlamadaService.registrar_respuesta(
                call_sid, "", RespuestaLlamada.RESPUESTA_BUZON
            )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(""),
            content_type="text/xml",
        )

    nombre_med      = request.GET.get("nombre_med", "su medicamento")
    instrucciones   = request.GET.get("instrucciones", "")
    nombre_paciente = request.GET.get("nombre_paciente", "")
    call_sid        = request.POST.get("CallSid", "")

    # Saludo natural — no lee las instrucciones en voz alta
    saludo_inicio = f"Hola{' ' + nombre_paciente if nombre_paciente else ''}, le llama Porvoz."
    saludo = f"{saludo_inicio} Es hora de tomar su {nombre_med}. ¿Ya lo tomó?"

    if call_sid:
        _conversaciones[call_sid] = {
            "history": f"Asistente: {saludo}",
            "nombre_med": nombre_med,
            "instrucciones": instrucciones,
            "nombre_paciente": nombre_paciente,
            "resultado": None,
            "turnos": 0,
        }

    base_url   = ProveedorVozService.get_base_url()
    gather_url = f"{base_url}/llamadas/webhook/gather/"
    return HttpResponse(
        ProveedorVozService.build_twiml_gather(saludo, gather_url),
        content_type="text/xml",
    )


@csrf_exempt
@require_http_methods(["POST"])
@verify_twilio_signature
def webhook_gather(request):
    """Recibe lo que dijo el paciente y responde con IA."""
    call_sid = request.POST.get("CallSid", "")
    speech   = request.POST.get("SpeechResult", "").strip()

    sesion = _conversaciones.get(
        call_sid, {"history": "", "nombre_med": "medicamento", "instrucciones": "", "nombre_paciente": "", "turnos": 0, "resultado": None}
    )
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
        _conversaciones.pop(call_sid, None)
        LlamadaService.registrar_respuesta(
            call_sid, historial,
            RespuestaLlamada.RESPUESTA_ATENDIDA, RespuestaLlamada.RESULTADO_SIN_CONFIRMAR,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_NO_ESCUCHO),
            content_type="text/xml",
        )

    historial_actualizado = (
        f"{historial}\nUsuario: {speech}" if historial else f"Usuario: {speech}"
    )

    # ------------------------------------------------------------------ #
    # 1. Detectar intención en el texto del paciente                       #
    # ------------------------------------------------------------------ #
    resultado_turno = _detectar_resultado(speech)
    if resultado_turno and resultado_sesion is None:
        resultado_sesion = resultado_turno

    # ------------------------------------------------------------------ #
    # 2. Cierre determinista — sin Gemini — cuando la intención es clara  #
    # ------------------------------------------------------------------ #
    if resultado_sesion == RespuestaLlamada.RESULTADO_CONFIRMADA:
        _conversaciones.pop(call_sid, None)
        LlamadaService.registrar_respuesta(
            call_sid, historial_actualizado,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_CONFIRMADO),
            content_type="text/xml",
        )

    if resultado_sesion == RespuestaLlamada.RESULTADO_NEGATIVA:
        _conversaciones.pop(call_sid, None)
        LlamadaService.registrar_respuesta(
            call_sid, historial_actualizado,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_NEGATIVO),
            content_type="text/xml",
        )

    if resultado_sesion == RespuestaLlamada.RESULTADO_DESPUES:
        _conversaciones.pop(call_sid, None)
        LlamadaService.registrar_respuesta(
            call_sid, historial_actualizado,
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
        _conversaciones.pop(call_sid, None)
        LlamadaService.registrar_respuesta(
            call_sid, historial_actualizado,
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

    try:
        respuesta_ia = ProveedorVozService.generar_respuesta_ia(
            speech, nombre_med, instrucciones, nombre_paciente, historial_reducido
        )
    except Exception as e:
        logger.error(f"[webhook_gather] Error Gemini: {e}")
        _conversaciones.pop(call_sid, None)
        LlamadaService.registrar_respuesta(
            call_sid, historial_actualizado,
            RespuestaLlamada.RESPUESTA_ATENDIDA, resultado_sesion,
        )
        return HttpResponse(
            ProveedorVozService.build_twiml_fin(ProveedorVozService.MSG_TIMEOUT),
            content_type="text/xml",
        )

    nuevo_historial = f"{historial_actualizado}\nAsistente: {respuesta_ia}"
    _conversaciones[call_sid] = {
        **sesion,
        "history": nuevo_historial,
        "turnos": turnos,
        "resultado": resultado_sesion,
    }

    # Si Gemini incluyó despedida, cerrar aquí
    _DESPEDIDAS = ("hasta luego", "adiós", "adios", "que tenga", "cuídese", "buen día", "buen dia")
    if any(d in respuesta_ia.lower() for d in _DESPEDIDAS):
        _conversaciones.pop(call_sid, None)
        LlamadaService.registrar_respuesta(
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


@csrf_exempt
@require_http_methods(["POST"])
@verify_twilio_signature
@deduplicate_webhook(key_func=lambda r: r.POST.get("CallSid"), ttl=600)
def webhook_status(request):
    """Twilio notifica el estado final de la llamada."""
    call_sid     = request.POST.get("CallSid", "")
    call_status  = request.POST.get("CallStatus", "")
    call_duration = request.POST.get("CallDuration", "0")

    try:
        duracion = int(call_duration)
    except (ValueError, TypeError):
        duracion = None

    if call_sid:
        LlamadaService.registrar_estado_final(call_sid, call_status, duracion)
        _conversaciones.pop(call_sid, None)

        if call_status in ("no-answer", "busy", "failed"):
            LlamadaService.registrar_respuesta(
                call_sid, "", RespuestaLlamada.RESPUESTA_NO_ATENDIDA
            )

    return HttpResponse(status=200)
