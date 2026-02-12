"""
URL configuration for porvoz project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # Autenticación y flujo principal de la webapp
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('paciente/', views.patient_dashboard, name='patient_dashboard'),

    # Admin y APIs existentes
    path('admin/', admin.site.urls),
    path('api/cuidadores/', include('cuidadores.urls')),
    path('api/pacientes/', include('pacientes.urls')),
    path('api/medicamentos/', include('medicamentos.urls')),
    path('api/recordatorios/', include('recordatorios.urls')),
    path('api/llamadas/', include('llamadas.urls')),
]
