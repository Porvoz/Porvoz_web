from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.health import health_check

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

# Custom error handlers — render templates/{400,403,404,500}.html
handler400 = "django.views.defaults.bad_request"
handler403 = "django.views.defaults.permission_denied"
handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"
