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
        
        if not nombre or not dosis:
            messages.error(request, "El nombre y la dosis son obligatorios.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO and not horario:
            messages.error(request, "Debes especificar un horario.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_CADA_X_HORAS and (not cada_x_horas or not hora_inicio):
            messages.error(request, "Debes especificar cada cuántas horas y la hora de inicio.")
        else:
            medicamento = Medicamento.objects.create(
                paciente=paciente,
                nombre=nombre,
                dosis=dosis,
                frecuencia_tipo=frecuencia_tipo,
                horario=horario or None,
                cada_x_horas=int(cada_x_horas) if cada_x_horas else None,
                hora_inicio=hora_inicio or None,
            )
            messages.success(request, f"Medicamento '{nombre}' agregado correctamente.")
            return redirect("listar_pacientes")
    
    context = {
        "perfil": perfil,
        "paciente": paciente,
    }
    return render(request, "medicamentos/agregar_medicamento.html", context)
