from django.urls import path

from . import views

urlpatterns = [
    path("", views.listar_pacientes_view, name="listar_pacientes"),
    path("agregar/", views.agregar_paciente_view, name="agregar_paciente"),
    path("<int:paciente_id>/", views.detalle_paciente_view, name="detalle_paciente"),
    path("<int:paciente_id>/historial-llamadas/", views.historial_llamadas_paciente_view, name="historial_llamadas_paciente"),
    path("<int:paciente_id>/editar/", views.editar_paciente_view, name="editar_paciente"),
    path("<int:paciente_id>/eliminar/", views.eliminar_paciente_view, name="eliminar_paciente"),
    path("<int:paciente_id>/enfermedad/agregar/", views.agregar_enfermedad_view, name="agregar_enfermedad"),
    path("<int:paciente_id>/enfermedad/<int:enfermedad_id>/editar/", views.editar_enfermedad_view, name="editar_enfermedad"),
]
