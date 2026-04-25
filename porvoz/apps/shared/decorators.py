"""
Decoradores para validación y rate limiting de webhooks Twilio
"""

import logging
import os
from functools import wraps

from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def verify_twilio_signature(view_func):
    """
    Verifica que el webhook viene realmente de Twilio.
    Usa el validador oficial del SDK de Twilio.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        validate_sign = os.getenv("TWILIO_VALIDATE_SIGNATURE", "true").lower()
        if validate_sign in ("0", "false", "no"):
            logger.warning("[Twilio] Validación de firma deshabilitada por TWILIO_VALIDATE_SIGNATURE")
            return view_func(request, *args, **kwargs)

        # Obtener auth token
        auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "") or os.getenv(
            "TWILIO_AUTH_TOKEN", ""
        )
        if not auth_token:
            logger.error("[Twilio] TWILIO_AUTH_TOKEN no configurado")
            if settings.DEBUG:
                logger.warning("[Twilio] DEBUG=True, se permite webhook sin token")
                return view_func(request, *args, **kwargs)
            return HttpResponse("Configuration error", status=500)

        # Obtener signature del header
        twilio_signature = request.META.get("HTTP_X_TWILIO_SIGNATURE", "")
        if not twilio_signature:
            logger.warning(
                f"[Twilio] Webhook sin X-Twilio-Signature: {request.path}"
            )
            if settings.DEBUG:
                logger.warning("[Twilio] DEBUG=True, se permite webhook sin signature")
                return view_func(request, *args, **kwargs)
            return HttpResponse("Forbidden: Missing signature", status=403)

        # Construir URL pública exacta usada por Twilio
        public_base_url = (os.getenv("TWILIO_BASE_URL") or os.getenv("BASE_URL") or "").rstrip("/")
        if public_base_url:
            request_url = f"{public_base_url}{request.get_full_path()}"
        else:
            request_url = request.build_absolute_uri()

        # Validar firma con SDK oficial
        from twilio.request_validator import RequestValidator

        validator = RequestValidator(auth_token)
        es_valida = validator.validate(request_url, request.POST, twilio_signature)

        if not es_valida:
            logger.error(
                "[Twilio] Signature mismatch. "
                f"URL validada: {request_url}, Path: {request.path}"
            )
            if settings.DEBUG:
                logger.warning("[Twilio] DEBUG=True, se permite webhook con signature inválida")
                return view_func(request, *args, **kwargs)
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
