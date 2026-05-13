"""
Django admin configuration for medicamentos app.
"""

from django.contrib import admin

from apps.medicamentos.models import HorarioMedicamento, Medicamento


class HorarioMedicamentoInline(admin.TabularInline):
    model = HorarioMedicamento
    extra = 1


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'paciente', 'dosis', 'activo')
    list_filter = ('activo', 'frecuencia_tipo')
    search_fields = ('nombre', 'paciente__nombre_apellido', 'dosis')
    inlines = [HorarioMedicamentoInline]


@admin.register(HorarioMedicamento)
class HorarioMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'hora')
    search_fields = ('medicamento__nombre',)
