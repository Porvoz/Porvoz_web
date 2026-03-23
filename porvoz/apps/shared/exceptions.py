"""
Excepciones personalizadas de Porvoz.

Uso en servicios:
    raise PacienteError("El nombre es obligatorio")

Uso en vistas:
    try:
        PacienteService.crear_paciente(...)
    except PacienteError as e:
        messages.error(request, str(e))
"""


class PorvozError(Exception):
    """Excepción base del proyecto."""
    pass


class PacienteError(PorvozError):
    """Errores relacionados con pacientes."""
    pass


class MedicamentoError(PorvozError):
    """Errores relacionados con medicamentos."""
    pass


class NotificacionError(PorvozError):
    """Errores relacionados con notificaciones."""
    pass


class PerfilError(PorvozError):
    """Errores relacionados con el perfil del usuario."""
    pass


class AuthError(PorvozError):
    """Errores relacionados con autenticación."""
    pass


class PlanError(PorvozError):
    """Errores relacionados con planes de suscripción."""
    pass
