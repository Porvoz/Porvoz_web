"""
Formularios para la app de pacientes.

Centraliza la validación de entradas del usuario,
liberando a las vistas de lógica de validación.
"""
from django import forms

from .models import Paciente, Enfermedad


class PacienteForm(forms.Form):
    nombre = forms.CharField(
        max_length=200,
        error_messages={"required": "El nombre es obligatorio."},
    )
    telefono = forms.CharField(
        max_length=30,
        required=False,
    )
    sexo = forms.ChoiceField(
        choices=[("", "No especificado")] + list(Paciente.SEXO_CHOICES),
        required=False,
    )
    fecha_nacimiento = forms.DateField(
        input_formats=["%Y-%m-%d"],
        required=False,
    )
    parentesco = forms.CharField(max_length=50, required=False)
    descripcion = forms.CharField(widget=forms.Textarea, required=False)
    notas = forms.CharField(widget=forms.Textarea, required=False)
    timezone = forms.CharField(max_length=50, required=False, initial="America/Bogota")
    es_usuario_mismo = forms.BooleanField(required=False)

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

    def clean_sexo(self):
        sexo = self.cleaned_data.get("sexo", "")
        opciones_validas = [k for k, _ in Paciente.SEXO_CHOICES] + [""]
        if sexo not in opciones_validas:
            return ""
        return sexo


class EnfermedadForm(forms.Form):
    nombre = forms.CharField(
        max_length=200,
        error_messages={"required": "El nombre de la condición es obligatorio."},
    )
    descripcion = forms.CharField(widget=forms.Textarea, required=False)
    diagnostico_fecha = forms.DateField(
        input_formats=["%Y-%m-%d"],
        required=False,
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre
