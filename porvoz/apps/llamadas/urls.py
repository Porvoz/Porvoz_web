from django.urls import path

from apps.llamadas import views

urlpatterns = [
    path("", views.historial_llamadas, name="historial_llamadas"),
    path("webhook/voice/", views.webhook_voice, name="llamadas_webhook_voice"),
    path("webhook/gather/", views.webhook_gather, name="llamadas_webhook_gather"),
    path("webhook/status/", views.webhook_status, name="llamadas_webhook_status"),
]
