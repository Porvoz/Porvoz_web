"""
Formularios para la app de medicamentos.

Centraliza la validación de entradas del usuario,
liberando a las vistas de lógica de validación.
"""

from django import forms

from .models import Medicamento


class MedicamentoForm(forms.Form):
    nombre = forms.CharField(
        max_length=200,
        error_messages={"required": "El nombre del medicamento es obligatorio."},
    )
    dosis = forms.CharField(
        max_length=100,
        error_messages={"required": "La dosis es obligatoria."},
    )
    frecuencia_tipo = forms.ChoiceField(
        choices=Medicamento.FRECUENCIA_CHOICES,
        initial=Medicamento.FRECUENCIA_HORARIO,
    )
    cada_x_horas = forms.IntegerField(min_value=1, max_value=24, required=False)
    hora_inicio = forms.TimeField(input_formats=["%H:%M"], required=False)
    fecha_inicio_tratamiento = forms.DateField(
        input_formats=["%Y-%m-%d"],
        required=False,
    )
    duracion_dias = forms.IntegerField(min_value=1, required=False)
    instrucciones_llamada = forms.CharField(
        max_length=200, required=False,
        widget=forms.TextInput(attrs={"maxlength": "200"}),
    )
    minutos_antes_llamada = forms.IntegerField(
        min_value=0, max_value=120, initial=0, required=False
    )
    max_reintentos = forms.IntegerField(
        min_value=0, max_value=3, initial=1, required=False,
        error_messages={"min_value": "Mínimo 0 reintentos.", "max_value": "Máximo 3 reintentos."},
    )
    minutos_entre_reintentos = forms.IntegerField(
        min_value=5, max_value=180, initial=30, required=False,
        error_messages={"min_value": "Mínimo 5 minutos entre reintentos.", "max_value": "Máximo 180 minutos."},
    )

    def clean(self):
        cleaned = super().clean()
        frecuencia = cleaned.get("frecuencia_tipo")

        if frecuencia == Medicamento.FRECUENCIA_CADA_X_HORAS:
            if not cleaned.get("cada_x_horas"):
                self.add_error("cada_x_horas", "Debes indicar cada cuántas horas.")
            if not cleaned.get("hora_inicio"):
                self.add_error("hora_inicio", "Debes indicar la hora de inicio.")

        # Las vistas pasan los horarios como campo extra fuera del form;
        # validamos su presencia en la vista. Aquí solo validamos campos del form.
        max_r = cleaned.get("max_reintentos")
        if max_r is not None and max_r > 3:
            self.add_error("max_reintentos", "Máximo 3 reintentos permitidos.")

        return cleaned

    def clean_nombre(self):
        return self.cleaned_data.get("nombre", "").strip()

    def clean_dosis(self):
        return self.cleaned_data.get("dosis", "").strip()
