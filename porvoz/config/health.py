from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok"})

def health_check(request):
    return JsonResponse({"status": "ok"})

def debug_csrf(request):
    return JsonResponse({"csrf": "ok"})
