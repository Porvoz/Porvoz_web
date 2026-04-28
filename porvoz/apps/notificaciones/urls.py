from django.urls import path

from . import views

urlpatterns = [
    path("", views.notifications_view, name="notifications"),
    path("marcar/<int:notif_id>/leida/", views.marcar_leida_view, name="marcar_notif_leida"),
    path("export/csv/", views.export_notifications_csv_view, name="export_notifications_csv"),
]
