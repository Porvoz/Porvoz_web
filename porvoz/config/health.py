import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def health_check(request):
    return JsonResponse({
        "status": "ok"
    }, status=200)


@require_http_methods(["GET"])
def debug_csrf(request):
    """Debug CSRF configuration — only available in non-production or with debug flag."""
    if not settings.DEBUG and not os.getenv("DJANGO_DEBUG_CSRF"):
        return JsonResponse({"error": "Debug endpoint disabled"}, status=403)

    return JsonResponse({
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
        "CSRF_TRUSTED_ORIGINS": settings.CSRF_TRUSTED_ORIGINS,
        "CSRF_COOKIE_SECURE": settings.CSRF_COOKIE_SECURE,
        "SESSION_COOKIE_SECURE": settings.SESSION_COOKIE_SECURE,
        "CSRF_COOKIE_HTTPONLY": settings.CSRF_COOKIE_HTTPONLY,
        "SECURE_PROXY_SSL_HEADER": settings.SECURE_PROXY_SSL_HEADER,
        "DEBUG": settings.DEBUG,
        "RAILWAY_PUBLIC_DOMAIN": os.getenv("RAILWAY_PUBLIC_DOMAIN", "NOT SET"),
        "DJANGO_ENVIRONMENT": os.getenv("DJANGO_ENVIRONMENT", "NOT SET"),
    }, status=200)
