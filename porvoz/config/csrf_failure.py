import contextlib
import os

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect


def csrf_failure(request, reason=""):
    """
    On CSRF mismatch, show the real reason in non-production or redirect in production.
    """
    # Show real error to diagnose — remove this once fixed
    if os.getenv("DJANGO_DEBUG_CSRF", ""):
        return HttpResponse(
            f"<h1>CSRF Failed</h1><p>Reason: {reason}</p>"
            f"<p>Origin: {request.META.get('HTTP_ORIGIN', 'N/A')}</p>"
            f"<p>Referer: {request.META.get('HTTP_REFERER', 'N/A')}</p>"
            f"<p>Host: {request.META.get('HTTP_HOST', 'N/A')}</p>",
            status=403,
            content_type="text/html",
        )

    referer = request.META.get("HTTP_REFERER") or "/"
    with contextlib.suppress(Exception):
        messages.error(request, "La sesión expiró. Por favor intenta de nuevo.")
    return HttpResponseRedirect(referer)
