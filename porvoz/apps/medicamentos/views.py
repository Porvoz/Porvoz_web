from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .models import Medicamento
from apps.pacientes.models import Paciente
from apps.core.models import Perfil


@login_required
def agregar_medicamento_view(request: HttpRequest, paciente_id: int) -> HttpResponse:
    """Vista para agregar un medicamento a un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        dosis = request.POST.get("dosis", "").strip()
        frecuencia_tipo = request.POST.get("frecuencia_tipo", Medicamento.FRECUENCIA_HORARIO)
        horario = request.POST.get("horario", "").strip()
        cada_x_horas = request.POST.get("cada_x_horas", "").strip()
        hora_inicio = request.POST.get("hora_inicio", "").strip()
        duracion_tipo = request.POST.get("duracion_tipo", "indefinido")
        duracion_dias_str = request.POST.get("duracion_dias", "").strip()
        
        if not nombre or not dosis:
            messages.error(request, "El nombre y la dosis son obligatorios.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO and not horario:
            messages.error(request, "Debes especificar un horario.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_CADA_X_HORAS and (not cada_x_horas or not hora_inicio):
            messages.error(request, "Debes especificar cada cuántas horas y la hora de inicio.")
        elif duracion_tipo == "dias" and (not duracion_dias_str or not duracion_dias_str.isdigit() or int(duracion_dias_str) < 1):
            messages.error(request, "Indica cuántos días de tratamiento (número mayor a 0).")
        else:
            duracion_dias = int(duracion_dias_str) if duracion_tipo == "dias" and duracion_dias_str else None
            medicamento = Medicamento.objects.create(
                paciente=paciente,
                nombre=nombre,
                dosis=dosis,
                frecuencia_tipo=frecuencia_tipo,
                horario=horario or None,
                cada_x_horas=int(cada_x_horas) if cada_x_horas else None,
                hora_inicio=hora_inicio or None,
                duracion_dias=duracion_dias,
            )
            messages.success(request, f"Medicamento '{nombre}' agregado correctamente.")
            return redirect("listar_pacientes")
    
    context = {
        "perfil": perfil,
        "paciente": paciente,
    }
    return render(request, "medicamentos/agregar_medicamento.html", context)


@login_required
def editar_medicamento_view(request: HttpRequest, paciente_id: int, medicamento_id: int) -> HttpResponse:
    """Vista para editar un medicamento de un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    medicamento = get_object_or_404(Medicamento, id=medicamento_id, paciente=paciente)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        dosis = request.POST.get("dosis", "").strip()
        frecuencia_tipo = request.POST.get("frecuencia_tipo", Medicamento.FRECUENCIA_HORARIO)
        horario = request.POST.get("horario", "").strip()
        cada_x_horas = request.POST.get("cada_x_horas", "").strip()
        hora_inicio = request.POST.get("hora_inicio", "").strip()
        duracion_tipo = request.POST.get("duracion_tipo", "indefinido")
        duracion_dias_str = request.POST.get("duracion_dias", "").strip()

        if not nombre or not dosis:
            messages.error(request, "El nombre y la dosis son obligatorios.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO and not horario:
            messages.error(request, "Debes especificar un horario.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_CADA_X_HORAS and (not cada_x_horas or not hora_inicio):
            messages.error(request, "Debes especificar cada cuántas horas y la hora de inicio.")
        elif duracion_tipo == "dias" and (not duracion_dias_str or not duracion_dias_str.isdigit() or int(duracion_dias_str) < 1):
            messages.error(request, "Indica cuántos días de tratamiento (número mayor a 0).")
        else:
            duracion_dias = int(duracion_dias_str) if duracion_tipo == "dias" and duracion_dias_str else None
            medicamento.nombre = nombre
            medicamento.dosis = dosis
            medicamento.frecuencia_tipo = frecuencia_tipo
            medicamento.horario = horario or None
            medicamento.cada_x_horas = int(cada_x_horas) if cada_x_horas else None
            medicamento.hora_inicio = hora_inicio or None
            medicamento.duracion_dias = duracion_dias
            medicamento.save()
            messages.success(request, f"Medicamento '{nombre}' actualizado correctamente.")
            return redirect("editar_paciente", paciente_id=paciente.id)

    context = {
        "perfil": perfil,
        "paciente": paciente,
        "medicamento": medicamento,
    }
    return render(request, "medicamentos/editar_medicamento.html", context)
