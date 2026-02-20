from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core import views as core_views
from apps.pacientes import views as pacientes_views
from apps.medicamentos import views as medicamentos_views


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # Autenticación y flujo principal
    path("login/", core_views.login_view, name="login"),
    path("register/", core_views.register_view, name="register"),
    path("logout/", core_views.logout_view, name="logout"),
    path("reset-password/", core_views.reset_password_view, name="reset_password"),
    path("perfil/editar/", core_views.complete_profile_view, name="edit_profile"),
    path("perfil/cambiar-contraseña/", core_views.change_password_view, name="change_password"),
    
    # Dashboards
    path("", core_views.dashboard_router, name="dashboard_router"),
    path("dashboard/", core_views.dashboard_unificado, name="dashboard"),
    path("notificaciones/", core_views.notifications_view, name="notifications"),
    path("planes/", core_views.plans_view, name="plans"),
    path("legal/", core_views.legal_info_view, name="legal_info"),
    path("guia/", core_views.guide_view, name="guide"),
    
    # Pacientes
    path("pacientes/", pacientes_views.listar_pacientes_view, name="listar_pacientes"),
    path("pacientes/agregar/", pacientes_views.agregar_paciente_view, name="agregar_paciente"),
    path("pacientes/<int:paciente_id>/editar/", pacientes_views.editar_paciente_view, name="editar_paciente"),
    path("pacientes/<int:paciente_id>/eliminar/", pacientes_views.eliminar_paciente_view, name="eliminar_paciente"),
    path("pacientes/<int:paciente_id>/enfermedad/agregar/", pacientes_views.agregar_enfermedad_view, name="agregar_enfermedad"),
    
    # Medicamentos
    path("medicamentos/agregar/<int:paciente_id>/", medicamentos_views.agregar_medicamento_view, name="agregar_medicamento"),
    
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
