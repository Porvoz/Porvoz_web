import json
import os
import urllib.parse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Reminder
from contacts.models import Contact
from calls.models import CallRecord


@csrf_exempt
@require_http_methods(["GET", "POST"])
def reminders_list(request):
    if request.method == "GET":
        reminders = Reminder.objects.select_related("contact").all()
        return JsonResponse([r.to_dict() for r in reminders], safe=False)

    data = json.loads(request.body)
    contact_id = data.get("contactId")
    title = (data.get("title") or "").strip()
    message = (data.get("message") or "").strip()
    scheduled_at = data.get("scheduledAt")

    if not all([contact_id, title, message, scheduled_at]):
        return JsonResponse(
            {"error": "Los campos contactId, título, mensaje y fecha programada son obligatorios"},
            status=400
        )

    try:
        contact = Contact.objects.get(pk=contact_id)
    except Contact.DoesNotExist:
        return JsonResponse({"error": "Contacto no encontrado"}, status=404)

    from django.utils.dateparse import parse_datetime
    scheduled_dt = parse_datetime(scheduled_at)

    if not scheduled_dt:
        return JsonResponse(
            {"error": "Formato de fecha inválido. Use formato ISO 8601"},
            status=400
        )

    reminder = Reminder.objects.create(
        contact=contact,
        title=title,
        message=message,
        scheduled_at=scheduled_dt,
        status="pending",
    )

    return JsonResponse(reminder.to_dict(), status=201)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def reminder_detail(request, pk):
    try:
        reminder = Reminder.objects.select_related("contact").get(pk=pk)
    except Reminder.DoesNotExist:
        return JsonResponse({"error": "Recordatorio no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(reminder.to_dict())

    if request.method == "PATCH":
        data = json.loads(request.body)

        if "title" in data:
            reminder.title = data["title"].strip()

        if "message" in data:
            reminder.message = data["message"].strip()

        if "scheduledAt" in data:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(data["scheduledAt"])
            if dt:
                reminder.scheduled_at = dt

        if "status" in data:
            reminder.status = data["status"]

        if "contactId" in data:
            try:
                reminder.contact = Contact.objects.get(pk=data["contactId"])
            except Contact.DoesNotExist:
                return JsonResponse({"error": "Contacto no encontrado"}, status=404)

        reminder.save()
        return JsonResponse(reminder.to_dict())

    reminder.delete()
    return JsonResponse({}, status=204)


@csrf_exempt
@require_http_methods(["POST"])
def trigger_call(request, pk):
    try:
        reminder = Reminder.objects.select_related("contact").get(pk=pk)
    except Reminder.DoesNotExist:
        return JsonResponse({"error": "Recordatorio no encontrado"}, status=404)

    if not reminder.contact or not reminder.contact.phone:
        return JsonResponse(
            {"error": "El contacto no tiene número de teléfono"},
            status=400
        )

    base_url = _get_base_url()

    try:
        from ai.twilio_gemini import get_twilio_client, get_twilio_phone

        client = get_twilio_client()
        phone = get_twilio_phone()

        call = client.calls.create(
            url=f"{base_url}/api/calls/webhook/voice?reminderId={reminder.id}&message={urllib.parse.quote(reminder.message or '')}",
            to=reminder.contact.phone,
            from_=phone,
            status_callback=f"{base_url}/api/calls/webhook/status",
            status_callback_method="POST",
        )

        CallRecord.objects.create(
            reminder=reminder,
            contact=reminder.contact,
            call_sid=call.sid,
            status="initiated",
        )

        Reminder.objects.filter(pk=pk).update(status="called")

        return JsonResponse({
            "success": True,
            "callSid": call.sid,
            "mensaje": "Llamada iniciada correctamente"
        })

    except Exception as e:
        CallRecord.objects.create(
            reminder=reminder,
            contact=reminder.contact,
            call_sid=None,
            status="failed",
        )

        Reminder.objects.filter(pk=pk).update(status="failed")

        return JsonResponse({
            "success": False,
            "callSid": None,
            "mensaje": str(e)
        }, status=500)


def _get_base_url():
    """
    Obtiene la URL base pública para que Twilio pueda acceder.
    Usa TWILIO_BASE_URL desde el .env.
    """
    base = os.environ.get("TWILIO_BASE_URL")

    if base:
        return base.rstrip("/")

    # fallback para desarrollo
    port = os.environ.get("PORT", "8000")
    return f"http://localhost:{port}"