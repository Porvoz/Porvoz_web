"""
Django admin configuration for admin_panel models
"""

from django.contrib import admin

from .models import CodigoAcceso, PagoHistorico, TicketSoporte


@admin.register(CodigoAcceso)
class CodigoAccesoAdmin(admin.ModelAdmin):
    list_display = [
        "codigo",
        "plan",
        "estado",
        "usuario_usado_por",
        "creado_en",
    ]
    list_filter = ["estado", "plan", "creado_en"]
    search_fields = ["codigo", "usuario_usado_por__username"]
    readonly_fields = ["codigo", "creado_en", "usado_en"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(PagoHistorico)
class PagoHistoricoAdmin(admin.ModelAdmin):
    list_display = ["usuario", "plan", "tipo_pago", "fecha_pago", "monto"]
    list_filter = ["tipo_pago", "plan", "fecha_pago"]
    search_fields = ["usuario__username", "referencia_pago"]
    readonly_fields = ["fecha_pago"]


@admin.register(TicketSoporte)
class TicketSoporteAdmin(admin.ModelAdmin):
    list_display = ["titulo", "usuario", "estado", "prioridad", "creado_en"]
    list_filter = ["estado", "prioridad", "creado_en"]
    search_fields = ["titulo", "usuario__username"]
    readonly_fields = ["creado_en", "actualizado_en"]
