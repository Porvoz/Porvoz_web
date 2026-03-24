"""
Formularios para la app de llamadas.

Disponible para futura UI manual de llamadas,
aunque generalmente se disparan automáticamente.
"""

from django import forms


class FiltroHistorialLlamadasForm(forms.Form):
    """Filtros para el historial de llamadas."""

    paciente = forms.IntegerField(required=False)
    estado = forms.ChoiceField(
        choices=[
            ("", "Todos"),
            ("programada", "Programada"),
            ("en_curso", "En curso"),
            ("completada", "Completada"),
            ("fallida", "Fallida"),
        ],
        required=False,
    )
    fecha_desde = forms.DateField(required=False)
    fecha_hasta = forms.DateField(required=False)
