"""
Context processors para que el sidebar y otras plantillas tengan siempre
el mismo contexto (p. ej. perfil) en todas las vistas.
"""

from .models import Perfil


def perfil_sidebar(request):
    """
    Añade `perfil` al contexto cuando el usuario está autenticado.
    Así el sidebar muestra siempre la foto y el nombre en todas las páginas
    (guía, legal, planes, etc.) sin que cada vista tenga que pasarlo.
    """
    if request.user.is_authenticated:
        perfil, _ = Perfil.objects.get_or_create(user=request.user)
        return {"perfil": perfil}
    return {"perfil": None}
