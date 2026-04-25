"""
Django admin configuration for llamadas app.
"""

from django.contrib import admin
from apps.llamadas.models import Llamada, RespuestaLlamada, AuditoriaLog


@admin.register(Llamada)
class LlamadaAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'paciente', 'estado', 'intentos')
    list_filter = ('estado',)
    search_fields = ('medicamento__nombre', 'paciente__nombre_apellido')


@admin.register(RespuestaLlamada)
class RespuestaLlamadaAdmin(admin.ModelAdmin):
    list_display = ('llamada', 'como_respondio', 'resultado')
    list_filter = ('como_respondio', 'resultado')
    search_fields = ('llamada__medicamento__nombre', 'transcripcion')


@admin.register(AuditoriaLog)
class AuditoriaLogAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion')
    list_filter = ('accion',)
    search_fields = ('usuario__username', 'descripcion')
