import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Contact


@csrf_exempt
@require_http_methods(["GET", "POST"])
def contacts_list(request):
    if request.method == "GET":
        contacts = Contact.objects.all()
        return JsonResponse([c.to_dict() for c in contacts], safe=False)

    data = json.loads(request.body)
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    notes = data.get("notes", "").strip() or None

    if not name or not phone:
        return JsonResponse({"error": "El nombre y el teléfono son obligatorios"}, status=400)

    contact = Contact.objects.create(name=name, phone=phone, notes=notes)
    return JsonResponse(contact.to_dict(), status=201)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def contact_detail(request, pk):
    try:
        contact = Contact.objects.get(pk=pk)
    except Contact.DoesNotExist:
        return JsonResponse({"error": "Contacto no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(contact.to_dict())

    if request.method == "PATCH":
        data = json.loads(request.body)
        if "name" in data:
            contact.name = data["name"].strip()
        if "phone" in data:
            contact.phone = data["phone"].strip()
        if "notes" in data:
            contact.notes = data["notes"].strip() or None
        contact.save()
        return JsonResponse(contact.to_dict())

    contact.delete()
    return JsonResponse({}, status=204)
