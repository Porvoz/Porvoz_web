import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.llamadas.models import Llamada, RespuestaLlamada
from apps.llamadas.services.llamada_service import LlamadaService
from apps.llamadas.services.proveedor_voz_service import ProveedorVozService

logger = logging.getLogger(__name__)

# Almacén en memoria de conversaciones activas {call_sid: {history, mensaje}}
_conversaciones = {}


@login_required
def historial_llamadas(request):
    """Historial global de llamadas del usuario."""
    qs = (
        Llamada.objects.filter(usuario=request.user)
        .select_related("paciente", "medicamento")
        .prefetch_related("respuesta")
    )

    estado = request.GET.get("estado", "")
    paciente_id = request.GET.get("paciente", "")
    if estado:
        qs = qs.filter(estado=estado)
    if paciente_id:
        qs = qs.filter(paciente_id=paciente_id)

    from apps.pacientes.models import Paciente
    pacientes = Paciente.objects.filter(usuario=request.user, activo=True).order_by("nombre")

    return render(request, "llamadas/historial.html", {
        "llamadas": qs,
        "pacientes": pacientes,
        "estado_filtro": estado,
        "paciente_filtro": paciente_id,
        "estados": Llamada.ESTADO_CHOICES,
        "total": qs.count(),
    })


# ------------------------------------------------------------------
# Webhooks Twilio (sin CSRF — Twilio no envía token)
# ------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["POST"])
def webhook_voice(request):
    """Inicio de llamada: genera saludo y espera respuesta del paciente."""
    llamada_id = request.GET.get("llamada_id", "")
    mensaje = request.GET.get("mensaje", "Recuerde tomar su medicamento.")
    call_sid = request.POST.get("CallSid", "")

    try:
        respuesta_ia = ProveedorVozService.generar_respuesta_ia("", mensaje, "")
    except Exception as e:
        logger.error(f"[webhook_voice] Error Gemini: {e}")
        respuesta_ia = f"Hola, le llamo de Porvoz para recordarle: {mensaje}. ¿Ya lo tomó?"

    if call_sid:
        _conversaciones[call_sid] = {"history": f"Asistente: {respuesta_ia}", "mensaje": mensaje}

    base_url = ProveedorVozService.get_base_url()
    gather_url = f"{base_url}/llamadas/webhook/gather/"
    twiml = ProveedorVozService.build_twiml_inicio(respuesta_ia, gather_url)
    return HttpResponse(twiml, content_type="text/xml")


@csrf_exempt
@require_http_methods(["POST"])
def webhook_gather(request):
    """Recibe lo que dijo el paciente y responde con IA."""
    call_sid = request.POST.get("CallSid", "")
    speech = request.POST.get("SpeechResult", "")

    sesion = _conversaciones.get(call_sid, {"history": "", "mensaje": ""})
    historial = sesion.get("history", "")
    mensaje = sesion.get("mensaje", "")

    historial_actualizado = f"{historial}\nUsuario: {speech}" if historial else f"Usuario: {speech}"

    try:
        respuesta_ia = ProveedorVozService.generar_respuesta_ia(speech, mensaje, historial_actualizado)
    except Exception as e:
        logger.error(f"[webhook_gather] Error Gemini: {e}")
        base_url = ProveedorVozService.get_base_url()
        gather_url = f"{base_url}/llamadas/webhook/gather/"
        return HttpResponse(
            ProveedorVozService.build_twiml_continuar("Disculpe, tuve un inconveniente. ¿Podría repetir?", gather_url),
            content_type="text/xml",
        )

    nuevo_historial = f"{historial_actualizado}\nAsistente: {respuesta_ia}"
    _conversaciones[call_sid] = {**sesion, "history": nuevo_historial}

    if call_sid:
        RespuestaLlamada.objects.filter(llamada__call_sid=call_sid).update(transcripcion=nuevo_historial)

    frases_despedida = ["hasta luego", "adiós", "adios", "que tenga", "cuídese", "buen día", "buen dia"]
    es_fin = any(f in respuesta_ia.lower() for f in frases_despedida)

    base_url = ProveedorVozService.get_base_url()
    if es_fin:
        _conversaciones.pop(call_sid, None)
        LlamadaService.registrar_respuesta(call_sid, nuevo_historial, RespuestaLlamada.RESPUESTA_ATENDIDA)
        return HttpResponse(ProveedorVozService.build_twiml_fin(respuesta_ia), content_type="text/xml")

    gather_url = f"{base_url}/llamadas/webhook/gather/"
    return HttpResponse(ProveedorVozService.build_twiml_continuar(respuesta_ia, gather_url), content_type="text/xml")


@csrf_exempt
@require_http_methods(["POST"])
def webhook_status(request):
    """Twilio notifica el estado final de la llamada."""
    call_sid = request.POST.get("CallSid", "")
    call_status = request.POST.get("CallStatus", "")
    call_duration = request.POST.get("CallDuration", "0")

    try:
        duracion = int(call_duration)
    except (ValueError, TypeError):
        duracion = None

    if call_sid:
        LlamadaService.registrar_estado_final(call_sid, call_status, duracion)
        _conversaciones.pop(call_sid, None)

        if call_status in ("no-answer", "busy", "failed"):
            LlamadaService.registrar_respuesta(call_sid, "", RespuestaLlamada.RESPUESTA_NO_ATENDIDA)

    return HttpResponse(status=200)
