from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.llamadas.health import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health_check"),
    # Apps
    path("", include("apps.autenticacion.urls")),
    path("", include("apps.usuarios.urls")),
    path("", include("apps.dashboard.urls")),
    path("", include("apps.legal.urls")),
    path("notificaciones/", include("apps.notificaciones.urls")),
    path("pacientes/", include("apps.pacientes.urls")),
    path("medicamentos/", include("apps.medicamentos.urls")),
    path("llamadas/", include("apps.llamadas.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
