from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import PorvozPasswordResetForm

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Recuperación de contraseña — 4 pasos con views built-in de Django
    path(
        "reset-password/",
        auth_views.PasswordResetView.as_view(
            template_name="autenticacion/reset_password.html",
            email_template_name="autenticacion/reset_password_email.txt",
            subject_template_name="autenticacion/reset_password_subject.txt",
            form_class=PorvozPasswordResetForm,
            success_url="/reset-password/done/",
        ),
        name="reset_password",
    ),
    path(
        "reset-password/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="autenticacion/reset_password_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset-password/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="autenticacion/reset_password_confirm.html",
            success_url="/reset-password/complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset-password/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="autenticacion/reset_password_complete.html",
        ),
        name="password_reset_complete",
    ),
]
