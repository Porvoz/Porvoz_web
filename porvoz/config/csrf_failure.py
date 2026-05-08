import contextlib

from django.contrib import messages
from django.http import HttpResponseRedirect


def csrf_failure(request, reason=""):
    """
    On CSRF mismatch (typically after login token rotation or a stale tab),
    redirect back to the same URL via GET so the browser receives a fresh
    token. The user sees a brief notice and can resubmit normally.
    """
    referer = request.META.get("HTTP_REFERER") or "/"
    with contextlib.suppress(Exception):
        messages.error(request, "La sesión expiró. Por favor intenta de nuevo.")
    return HttpResponseRedirect(referer)
