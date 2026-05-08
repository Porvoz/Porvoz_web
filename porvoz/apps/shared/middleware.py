"""
Shared middleware for Porvoz.
"""

import threading
import uuid

_local = threading.local()


def get_correlation_id() -> str | None:
    """Returns the current request's correlation ID (thread-local)."""
    return getattr(_local, "correlation_id", None)


class CorrelationIdMiddleware:
    """
    Propagates or generates a correlation ID for each request.
    Reads X-Correlation-Id from incoming headers (useful when called from another
    service or from Twilio retry). Falls back to a new UUID4.
    Injects the ID back into the response header so clients can correlate logs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        correlation_id = (
            request.headers.get("X-Correlation-Id")
            or request.META.get("HTTP_X_CORRELATION_ID")
            or str(uuid.uuid4())
        )
        _local.correlation_id = correlation_id
        response = self.get_response(request)
        response["X-Correlation-Id"] = correlation_id
        return response
