"""
Decoradores para validación y rate limiting de webhooks Twilio
"""

import hashlib
import hmac
import logging
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse

logger = logging.getLogger(__name__)


def verify_twilio_signature(view_func):
    """
    Verifica que el webhook viene realmente de Twilio.
    Compara X-Twilio-Signature con HMAC-SHA1 del body.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Obtener auth token
        auth_token = settings.TWILIO_AUTH_TOKEN
        if not auth_token:
            logger.error("[Twilio] TWILIO_AUTH_TOKEN no configurado")
            return HttpResponse("Configuration error", status=500)

        # Obtener signature del header
        twilio_signature = request.META.get("HTTP_X_TWILIO_SIGNATURE", "")
        if not twilio_signature:
            logger.warning(
                f"[Twilio] Webhook sin X-Twilio-Signature: {request.path}"
            )
            return HttpResponse("Forbidden: Missing signature", status=403)

        # Construir URL base para validación
        base_url = request.build_absolute_uri(request.path)

        # Construir request body con parámetros ordenados
        post_params = request.POST.dict()
        param_str = "".join(f"{k}{v}" for k, v in sorted(post_params.items()))
        request_url = base_url + param_str

        # Calcular HMAC esperado
        expected_signature = hmac.new(
            auth_token.encode(),
            request_url.encode(),
            hashlib.sha1,
        ).digest()
        expected_signature_b64 = __import__(
            "base64"
        ).b64encode(expected_signature).decode()

        # Comparar (timing-safe)
        if not hmac.compare_digest(
            twilio_signature, expected_signature_b64
        ):
            logger.error(
                f"[Twilio] Signature mismatch. "
                f"Expected: {expected_signature_b64}, "
                f"Got: {twilio_signature}"
            )
            return HttpResponse("Forbidden: Invalid signature", status=403)

        logger.info(f"[Twilio] Signature válida: {request.path}")
        return view_func(request, *args, **kwargs)

    return wrapper


def rate_limit_by_key(key_func=None, rate="10/s"):
    """
    Rate limit por clave. Formato: "10/s", "5/m", etc.
    key_func(request) → retorna la clave de rate limit (ej: call_sid)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Parsear rate
            count_str, period_str = rate.split("/")
            count = int(count_str)
            period_seconds = {"s": 1, "m": 60, "h": 3600}[period_str]

            # Obtener clave
            key = key_func(request) if key_func else request.META.get("REMOTE_ADDR")
            cache_key = f"ratelimit:{key}"

            # Incrementar counter
            current = cache.get(cache_key, 0)
            if current >= count:
                logger.warning(
                    f"[RateLimit] Blocked {key}: {current}/{count} en {period_seconds}s"
                )
                return HttpResponse(
                    "Rate limit exceeded", status=429
                )

            cache.set(cache_key, current + 1, period_seconds)
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def deduplicate_webhook(key_func=None, ttl=300):
    """
    Previene procesar el mismo webhook 2 veces (idempotencia).
    key_func(request) → clave única (ej: call_sid)
    ttl: segundos para mantener deduplicación
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Obtener clave
            key = key_func(request) if key_func else request.POST.get("CallSid")
            if not key:
                logger.warning("[Deduplicate] No key provided")
                return view_func(request, *args, **kwargs)

            # Chequear si ya procesamos
            dedup_key = f"webhook:{key}"
            if cache.get(dedup_key):
                logger.warning(f"[Deduplicate] Webhook duplicado: {key}")
                # Retornar 200 para que Twilio no reintenté
                return HttpResponse("OK (duplicate)", status=200)

            # Marcar como procesado
            cache.set(dedup_key, True, ttl)

            # Procesar
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
