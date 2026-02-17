from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core import views as core_views


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # Autenticación y flujo principal
    path("login/", core_views.login_view, name="login"),
    path("register/", core_views.register_view, name="register"),
    path("logout/", core_views.logout_view, name="logout"),
    path("perfil/editar/", core_views.complete_profile_view, name="edit_profile"),
    
    # Dashboards
    path("", core_views.dashboard_router, name="dashboard_router"),
    path("cuidador/", core_views.caregiver_dashboard, name="dashboard"),
    path("cuidador/pacientes/", core_views.caregiver_patients_view, name="caregiver_patients"),
    path("paciente/", core_views.patient_dashboard, name="patient_dashboard"),
    path("paciente/datos-medicos/", core_views.medical_data_view, name="medical_data"),
    path("notificaciones/", core_views.notifications_view, name="notifications"),
    
    # APIs de microapps (vacías por ahora)
    path("api/cuidadores/", include("apps.cuidadores.urls")),
    path("api/pacientes/", include("apps.pacientes.urls")),
    path("api/medicamentos/", include("apps.medicamentos.urls")),
    path("api/recordatorios/", include("apps.recordatorios.urls")),
    path("api/llamadas/", include("apps.llamadas.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
