from django.urls import path
from . import views

urlpatterns = [
    path("calls", views.calls_list),
    path("healthz", views.health_check),
    path("calls/webhook/voice", views.webhook_voice),
    path("calls/webhook/gather", views.webhook_gather),
    path("calls/webhook/status", views.webhook_status),
]
