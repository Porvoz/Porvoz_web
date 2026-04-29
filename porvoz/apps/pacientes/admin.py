"""
Django admin configuration for pacientes app.
"""

from django.contrib import admin

from apps.pacientes.models import Enfermedad, Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono')
    list_filter = ('activo',)
    search_fields = ('usuario__username', 'apodo')


@admin.register(Enfermedad)
class EnfermedadAdmin(admin.ModelAdmin):
    list_display = ('paciente',)
    list_filter = ('activa',)
    search_fields = ('paciente__usuario__username',)
