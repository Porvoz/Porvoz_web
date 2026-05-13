from django.urls import path

from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("codigos/crear/", views.crear_codigos, name="crear_codigos"),
    path("codigos/ver/", views.ver_codigos, name="ver_codigos"),
    path("planes/", views.gestionar_planes, name="gestionar_planes"),
    path("usuarios/", views.ver_usuarios, name="admin_usuarios"),
    path("usuarios/crear/", views.crear_usuario_admin, name="crear_usuario_admin"),
    path("usuarios/<int:usuario_id>/editar/", views.editar_usuario, name="editar_usuario"),
    path("pagos/", views.historial_pagos, name="historial_pagos"),
    path("pagos/<int:pago_id>/", views.pago_detalle, name="pago_detalle"),
    path("pagos/crear/", views.crear_pago_manual, name="crear_pago_manual"),
    path("tickets/", views.tickets_soporte, name="tickets_soporte"),
    path("tickets/<int:ticket_id>/", views.ticket_detalle, name="ticket_detalle"),
    path("contacto/", views.contactar_soporte, name="contactar_soporte"),
    # Rutas para que usuarios normales vean sus tickets
    path("mis-tickets/", views.mis_tickets, name="mis_tickets"),
    path("mis-tickets/<int:ticket_id>/", views.mi_ticket_detalle, name="mi_ticket_detalle"),
]
