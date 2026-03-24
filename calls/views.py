from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CallRecord

_conversation_store = {}


@require_http_methods(["GET"])
def calls_list(request):
    calls = CallRecord.objects.select_related("contact").all()
    return JsonResponse([c.to_dict() for c in calls], safe=False)


@require_http_methods(["GET"])
def health_check(request):
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_http_methods(["POST"])
def webhook_voice(request):
    reminder_id = request.GET.get("reminderId")
    message = request.GET.get("message", "Tienes un recordatorio pendiente.")

    call_sid = request.POST.get("CallSid", "")

    from ai.twilio_gemini import generate_ai_response, build_twiml, get_base_url
    import logging

    logger = logging.getLogger(__name__)

    try:
        ai_response = generate_ai_response("", message, "")
    except Exception as e:
        logger.error(f"[Voice webhook] Error generando respuesta: {e}")
        ai_response = f"Hola, le llamo de Porvoz para recordarle: {message}. ¿Pudo realizar esta acción?"

    if call_sid:
        _conversation_store[call_sid] = {
            "history": f"Asistente: {ai_response}",
            "message": message,
        }
        if reminder_id:
            try:
                CallRecord.objects.filter(call_sid=call_sid).update(transcript=f"Asistente: {ai_response}")
            except Exception:
                pass

    base_url = get_base_url()
    gather_action = f"{base_url}/api/calls/webhook/gather"

    twiml = build_twiml(ai_response, gather_action)
    return HttpResponse(twiml, content_type="text/xml")


@csrf_exempt
@require_http_methods(["POST"])
def webhook_gather(request):
    call_sid = request.POST.get("CallSid", "")
    speech_result = request.POST.get("SpeechResult", "")

    from ai.twilio_gemini import generate_ai_response, build_twiml, build_end_twiml, get_base_url
    import logging

    logger = logging.getLogger(__name__)

    session = _conversation_store.get(call_sid, {"history": "", "message": ""})
    current_history = session.get("history", "")
    reminder_message = session.get("message", "")

    updated_history = f"{current_history}\nUsuario: {speech_result}" if current_history else f"Usuario: {speech_result}"

    base_url = get_base_url()
    gather_action = f"{base_url}/api/calls/webhook/gather"

    try:
        ai_response = generate_ai_response(speech_result, reminder_message, updated_history)
    except Exception as e:
        logger.error(f"[Gather webhook] Error generando respuesta con Gemini: {e}")
        twiml = build_twiml("Disculpe, tuve un inconveniente. ¿Podría repetir lo que me dijo?", gather_action)
        return HttpResponse(twiml, content_type="text/xml")

    new_history = f"{updated_history}\nAsistente: {ai_response}"
    _conversation_store[call_sid] = {**session, "history": new_history}

    if call_sid:
        try:
            CallRecord.objects.filter(call_sid=call_sid).update(transcript=new_history)
        except Exception:
            pass

    farewell_phrases = ["hasta luego", "adiós", "adios", "que tenga", "cuídese", "cuidese", "buen día", "buen dia"]
    is_ending = any(p in ai_response.lower() for p in farewell_phrases)

    if is_ending:
        _conversation_store.pop(call_sid, None)
        twiml = build_end_twiml(ai_response)
        return HttpResponse(twiml, content_type="text/xml")

    twiml = build_twiml(ai_response, gather_action)
    return HttpResponse(twiml, content_type="text/xml")


@csrf_exempt
@require_http_methods(["POST"])
def webhook_status(request):
    call_sid = request.POST.get("CallSid", "")
    call_status = request.POST.get("CallStatus", "")
    call_duration = request.POST.get("CallDuration", "0")

    try:
        duration = int(call_duration)
    except (ValueError, TypeError):
        duration = None

    if call_sid:
        CallRecord.objects.filter(call_sid=call_sid).update(
            status=call_status or "completed",
            duration=duration,
        )
        _conversation_store.pop(call_sid, None)

    return HttpResponse(status=200)
