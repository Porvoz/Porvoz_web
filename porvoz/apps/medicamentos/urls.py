from django.urls import path

from . import views

urlpatterns = [
    path("agregar/<int:paciente_id>/", views.agregar_medicamento_view, name="agregar_medicamento"),
    path(
        "<int:paciente_id>/<int:medicamento_id>/editar/",
        views.editar_medicamento_view,
        name="editar_medicamento",
    ),
    path(
        "<int:paciente_id>/<int:medicamento_id>/toggle/",
        views.toggle_medicamento_view,
        name="toggle_medicamento",
    ),
    path(
        "<int:paciente_id>/<int:medicamento_id>/eliminar/",
        views.eliminar_medicamento_view,
        name="eliminar_medicamento",
    ),
]
