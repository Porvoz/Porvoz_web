from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_router, name="dashboard_router"),
    path("dashboard/", views.dashboard_unificado, name="dashboard"),
]
