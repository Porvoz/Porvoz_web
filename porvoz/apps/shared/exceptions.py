"""
Excepciones personalizadas de Porvoz.

Uso en servicios:
    raise NotificacionError("No se pudo crear la notificación")

Uso en vistas:
    try:
        NotificacionService.crear(...)
    except NotificacionError as e:
        messages.error(request, str(e))
"""


class PorvozError(Exception):
    """Excepción base del proyecto."""

    pass


class NotificacionError(PorvozError):
    """Errores relacionados con notificaciones."""

    pass
