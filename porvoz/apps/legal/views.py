from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def legal_info_view(request: HttpRequest) -> HttpResponse:
    """Vista índice de información legal (enlaces a términos, privacidad, contacto)."""
    return render(request, "legal/legal_info.html")


def terms_view(request: HttpRequest) -> HttpResponse:
    """Términos y Condiciones."""
    return render(request, "legal/terms.html")


def privacy_view(request: HttpRequest) -> HttpResponse:
    """Política de Privacidad."""
    return render(request, "legal/privacy.html")


def contact_view(request: HttpRequest) -> HttpResponse:
    """Contacto."""
    return render(request, "legal/contact.html")


def guide_view(request: HttpRequest) -> HttpResponse:
    """Vista para mostrar la guía rápida y preguntas frecuentes."""
    return render(request, "legal/guide.html")
