from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("codigos/crear/", views.crear_codigos, name="crear_codigos"),
    path("codigos/ver/", views.ver_codigos, name="ver_codigos"),
    path("usuarios/", views.ver_usuarios, name="admin_usuarios"),
    path("usuarios/crear/", views.crear_usuario_admin, name="crear_usuario_admin"),
    path("usuarios/<int:usuario_id>/editar/", views.editar_usuario, name="editar_usuario"),
    path("pagos/", views.historial_pagos, name="historial_pagos"),
    path("pagos/crear/", views.crear_pago_manual, name="crear_pago_manual"),
    path("tickets/", views.tickets_soporte, name="tickets_soporte"),
    path("tickets/<int:ticket_id>/", views.ticket_detalle, name="ticket_detalle"),
    path("contacto/", views.contactar_soporte, name="contactar_soporte"),
]
