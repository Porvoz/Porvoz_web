from django.db import models


class Cuidador(models.Model):
    """
    Placeholder para futuros campos específicos de cuidadores.
    Por ahora usamos únicamente Perfil en apps.core.
    """

    created_at = models.DateTimeField(auto_now_add=True)


