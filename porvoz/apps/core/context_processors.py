"""
Context processors para que el sidebar y otras plantillas tengan siempre
el mismo contexto (p. ej. perfil) en todas las vistas.
"""

from .models import Perfil


def perfil_sidebar(request):
    """
    Añade `perfil` y `no_leidas_notificaciones` al contexto cuando el usuario está autenticado.
    Así el sidebar muestra siempre la foto, el nombre y el badge de notificaciones no leídas.
    """
    if request.user.is_authenticated:
        perfil, _ = Perfil.objects.get_or_create(user=request.user)
        from apps.notificaciones.models import Notificacion

        no_leidas = Notificacion.objects.filter(
            usuario=request.user, leida=False
        ).count()
        return {"perfil": perfil, "no_leidas_notificaciones": no_leidas}
    return {"perfil": None, "no_leidas_notificaciones": 0}
