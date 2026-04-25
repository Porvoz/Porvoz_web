"""
Django admin configuration for core app (Perfil model).
"""

from django.contrib import admin
from apps.core.models import Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('plan',)
    list_filter = ('plan',)
    search_fields = ('usuario__username', 'usuario__email')
