from django.urls import path

from apps.llamadas import views

urlpatterns = [
    path("", views.historial_llamadas, name="historial_llamadas"),
    path("<int:llamada_id>/cancelar/", views.cancelar_llamada, name="cancelar_llamada"),
    path("exportar/pdf/", views.exportar_historial_pdf, name="exportar_historial_pdf"),
    path("webhook/voice/", views.webhook_voice, name="llamadas_webhook_voice"),
    path("webhook/gather/", views.webhook_gather, name="llamadas_webhook_gather"),
    path("webhook/status/", views.webhook_status, name="llamadas_webhook_status"),
]
