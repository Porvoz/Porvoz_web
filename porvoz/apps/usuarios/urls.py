from django.urls import path

from . import views

urlpatterns = [
    path("perfil/editar/", views.complete_profile_view, name="edit_profile"),
    path(
        "perfil/cambiar-contraseña/", views.change_password_view, name="change_password"
    ),
    path("planes/", views.plans_view, name="plans"),
]
