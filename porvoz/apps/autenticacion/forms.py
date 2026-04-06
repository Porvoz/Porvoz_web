"""
Formularios para la app de autenticación.

Centraliza la validación de registro e inicio de sesión,
liberando a las vistas de lógica de validación.
"""

from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        error_messages={"required": "El usuario es obligatorio."},
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={"required": "La contraseña es obligatoria."},
    )


class RegistroForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        error_messages={"required": "El nombre es obligatorio."},
    )
    last_name = forms.CharField(
        max_length=150,
        error_messages={"required": "Los apellidos son obligatorios."},
    )
    username = forms.CharField(
        max_length=150,
        error_messages={"required": "El nombre de usuario es obligatorio."},
    )
    email = forms.EmailField(
        error_messages={"required": "El correo es obligatorio."},
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        error_messages={
            "required": "La contraseña es obligatoria.",
            "min_length": "La contraseña debe tener al menos 8 caracteres.",
        },
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={"required": "Confirma tu contraseña."},
    )
    date_of_birth = forms.DateField(
        input_formats=["%Y-%m-%d"],
        required=False,
    )
    city = forms.CharField(max_length=100, required=False)
    emergency_contact_name = forms.CharField(max_length=150, required=False)

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        password2 = cleaned.get("password2")
        if password and password2 and password != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned


class CambiarPasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={"required": "La contraseña actual es obligatoria."},
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        error_messages={
            "required": "La nueva contraseña es obligatoria.",
            "min_length": "La nueva contraseña debe tener al menos 8 caracteres.",
        },
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={"required": "Confirma tu nueva contraseña."},
    )

    def clean(self):
        cleaned = super().clean()
        new_password = cleaned.get("new_password")
        confirm = cleaned.get("confirm_password")
        old_password = cleaned.get("old_password")

        if new_password and confirm and new_password != confirm:
            self.add_error("confirm_password", "Las contraseñas no coinciden.")

        if new_password and old_password and new_password == old_password:
            self.add_error(
                "new_password", "La nueva contraseña debe ser diferente a la actual."
            )

        return cleaned
