"""
URL configuration for porvoz project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('api/cuidadores/', include('cuidadores.urls')),
    path('api/pacientes/', include('pacientes.urls')),
    path('api/medicamentos/', include('medicamentos.urls')),
    path('api/recordatorios/', include('recordatorios.urls')),
    path('api/llamadas/', include('llamadas.urls')),
]
