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
    instrucciones_llamada = forms.CharField(widget=forms.Textarea, required=False)
    minutos_antes_llamada = forms.IntegerField(
        min_value=0, max_value=120, initial=0, required=False
    )

    def clean(self):
        cleaned = super().clean()
        frecuencia = cleaned.get("frecuencia_tipo")

        if frecuencia == Medicamento.FRECUENCIA_CADA_X_HORAS:
            if not cleaned.get("cada_x_horas"):
                self.add_error("cada_x_horas", "Debes indicar cada cuántas horas.")
            if not cleaned.get("hora_inicio"):
                self.add_error("hora_inicio", "Debes indicar la hora de inicio.")

        return cleaned

    def clean_nombre(self):
        return self.cleaned_data.get("nombre", "").strip()

    def clean_dosis(self):
        return self.cleaned_data.get("dosis", "").strip()
