"""
Django admin configuration for notificaciones app.
"""

from django.contrib import admin
from apps.notificaciones.models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'prioridad', 'usuario', 'leida')
    list_filter = ('tipo', 'prioridad', 'leida')
    search_fields = ('titulo', 'mensaje', 'usuario__username', 'paciente__nombre_apellido')
