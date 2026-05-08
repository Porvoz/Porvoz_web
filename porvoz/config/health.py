"""
Health check para monitoreo de servicios
"""

import logging
from datetime import datetime

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def health_check(request):
    """
    GET /api/health/

    Verifica estado de:
    - Base de datos
    - Cache
    - Twilio (test connection)
    - Gemini (test connection)

    Returns 200 si todo está bien, 503 si algo falla.
    """
    status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "unknown",
            "cache": "unknown",
            "celery": "unknown",
            "twilio": "unknown",
            "gemini": "unknown",
        },
    }

    # 1. Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status["services"]["database"] = "ok"
    except Exception as e:
        logger.error(f"[Health] Database error: {e}")
        status["services"]["database"] = "error"
        status["status"] = "degraded"

    # 2. Cache
    try:
        from django.core.cache import cache
        cache.set("__health_check__", "ok", 10)
        val = cache.get("__health_check__")
        status["services"]["cache"] = "ok" if val == "ok" else "error"
        if val != "ok":
            status["status"] = "degraded"
    except Exception as e:
        logger.error(f"[Health] Cache error: {e}")
        status["services"]["cache"] = "error"
        status["status"] = "degraded"

    # 3. Celery worker
    try:
        from config.celery import app as celery_app
        insp = celery_app.control.inspect(timeout=2)
        active = insp.active()
        status["services"]["celery"] = "ok" if active else "no_workers"
        if not active:
            status["status"] = "degraded"
    except Exception as e:
        logger.error(f"[Health] Celery error: {e}")
        status["services"]["celery"] = "error"
        status["status"] = "degraded"

    # 4. Twilio
    try:
        from apps.llamadas.services.proveedor_voz_service import ProveedorVozService
        client = ProveedorVozService.get_twilio_client()
        # Simple test: obtener account info
        account = client.api.accounts.get()
        if account:
            status["services"]["twilio"] = "ok"
        else:
            raise Exception("No account found")
    except Exception as e:
        logger.error(f"[Health] Twilio error: {e}")
        status["services"]["twilio"] = "error"
        status["status"] = "degraded"

    # 4. Gemini
    try:
        from apps.llamadas.services.proveedor_voz_service import ProveedorVozService
        model = ProveedorVozService._get_gemini_model()
        # Simple test: generar contenido vacío (fallará pero probará conexión)
        response = model.generate_content(".")
        if response:
            status["services"]["gemini"] = "ok"
    except Exception as e:
        logger.error(f"[Health] Gemini error: {e}")
        status["services"]["gemini"] = "error"
        status["status"] = "degraded"

    # Retornar con status HTTP apropiado
    http_status = 200 if status["status"] == "ok" else 503
    return JsonResponse(status, status=http_status)
