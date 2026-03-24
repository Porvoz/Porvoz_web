from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .models import Medicamento, HorarioMedicamento
from .services import MedicamentoService
from apps.pacientes.models import Paciente
from apps.core.models import Perfil
from apps.notificaciones.services import NotificacionService


@login_required
def agregar_medicamento_view(request: HttpRequest, paciente_id: int) -> HttpResponse:
    """Vista para agregar un medicamento a un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        dosis = request.POST.get("dosis", "").strip()
        frecuencia_tipo = request.POST.get("frecuencia_tipo", Medicamento.FRECUENCIA_HORARIO)
        horarios_raw = [h.strip() for h in request.POST.getlist("horario") if h and h.strip()]
        cada_x_horas = request.POST.get("cada_x_horas", "").strip()
        hora_inicio = request.POST.get("hora_inicio", "").strip()
        fecha_inicio_str = request.POST.get("fecha_inicio_tratamiento", "").strip()
        duracion_tipo = request.POST.get("duracion_tipo", "indefinido")
        duracion_dias_str = request.POST.get("duracion_dias", "").strip()
        instrucciones_llamada = request.POST.get("instrucciones_llamada", "").strip()
        minutos_antes_str = request.POST.get("minutos_antes_llamada", "0").strip()
        
        if not nombre or not dosis:
            messages.error(request, "El nombre y la dosis son obligatorios.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO and not horarios_raw:
            messages.error(request, "Debes especificar al menos un horario de toma.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_CADA_X_HORAS and (not cada_x_horas or not hora_inicio):
            messages.error(request, "Debes especificar cada cuántas horas y la hora de inicio.")
        elif duracion_tipo == "dias" and (not duracion_dias_str or not duracion_dias_str.isdigit() or int(duracion_dias_str) < 1):
            messages.error(request, "Indica cuántos días de tratamiento (número mayor a 0).")
        else:
            duracion_dias = int(duracion_dias_str) if duracion_tipo == "dias" and duracion_dias_str else None
            minutos_antes = min(120, max(0, int(minutos_antes_str))) if minutos_antes_str.isdigit() else 0
            
            medicamento = MedicamentoService.crear_medicamento(
                paciente=paciente,
                nombre=nombre,
                dosis=dosis,
                frecuencia_tipo=frecuencia_tipo,
                horarios=horarios_raw,
                cada_x_horas=int(cada_x_horas) if cada_x_horas else None,
                hora_inicio=hora_inicio or None,
                fecha_inicio=fecha_inicio_str,
                duracion_dias=duracion_dias,
                instrucciones_llamada=instrucciones_llamada,
                minutos_antes=minutos_antes,
            )
            NotificacionService.crear_notificacion_sistema(
                usuario=request.user,
                titulo=f'Medicamento "{nombre}" agregado para {paciente.get_display_nombre()}',
                paciente=paciente,
                medicamento=medicamento,
            )
            messages.success(request, f"Medicamento '{nombre}' agregado correctamente.")
            return redirect("detalle_paciente", paciente_id=paciente.id)
    
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
        horarios_raw = [h.strip() for h in request.POST.getlist("horario") if h and h.strip()]
        cada_x_horas = request.POST.get("cada_x_horas", "").strip()
        hora_inicio = request.POST.get("hora_inicio", "").strip()
        fecha_inicio_str = request.POST.get("fecha_inicio_tratamiento", "").strip()
        duracion_tipo = request.POST.get("duracion_tipo", "indefinido")
        duracion_dias_str = request.POST.get("duracion_dias", "").strip()
        instrucciones_llamada = request.POST.get("instrucciones_llamada", "").strip()
        minutos_antes_str = request.POST.get("minutos_antes_llamada", "0").strip()

        if not nombre or not dosis:
            messages.error(request, "El nombre y la dosis son obligatorios.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO and not horarios_raw:
            messages.error(request, "Debes especificar al menos un horario de toma.")
        elif frecuencia_tipo == Medicamento.FRECUENCIA_CADA_X_HORAS and (not cada_x_horas or not hora_inicio):
            messages.error(request, "Debes especificar cada cuántas horas y la hora de inicio.")
        elif duracion_tipo == "dias" and (not duracion_dias_str or not duracion_dias_str.isdigit() or int(duracion_dias_str) < 1):
            messages.error(request, "Indica cuántos días de tratamiento (número mayor a 0).")
        else:
            duracion_dias = int(duracion_dias_str) if duracion_tipo == "dias" and duracion_dias_str else None
            minutos_antes = min(120, max(0, int(minutos_antes_str))) if minutos_antes_str.isdigit() else 0
            
            MedicamentoService.actualizar_medicamento(
                medicamento=medicamento,
                nombre=nombre,
                dosis=dosis,
                frecuencia_tipo=frecuencia_tipo,
                horarios=horarios_raw,
                cada_x_horas=int(cada_x_horas) if cada_x_horas else None,
                hora_inicio=hora_inicio or None,
                fecha_inicio=fecha_inicio_str,
                duracion_dias=duracion_dias,
                instrucciones_llamada=instrucciones_llamada,
                minutos_antes=minutos_antes,
            )
            NotificacionService.crear_notificacion_sistema(
                usuario=request.user,
                titulo=f'Medicamento "{nombre}" actualizado para {paciente.get_display_nombre()}',
                paciente=paciente,
                medicamento=medicamento,
            )
            messages.success(request, f"Medicamento '{nombre}' actualizado correctamente.")
            return redirect("detalle_paciente", paciente_id=paciente.id)

    context = {
        "perfil": perfil,
        "paciente": paciente,
        "medicamento": medicamento,
    }
    return render(request, "medicamentos/editar_medicamento.html", context)


@login_required
def toggle_medicamento_view(request: HttpRequest, paciente_id: int, medicamento_id: int) -> HttpResponse:
    """POST: activar o desactivar un medicamento. Redirige al detalle del paciente."""
    if request.method != "POST":
        return redirect("detalle_paciente", paciente_id=paciente_id)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    medicamento = get_object_or_404(Medicamento, id=medicamento_id, paciente=paciente)
    medicamento.activo = MedicamentoService.toggle_medicamento(medicamento)
    estado = "activado" if medicamento.activo else "desactivado"
    NotificacionService.crear_notificacion_sistema(
        usuario=request.user,
        titulo=f'Recordatorio "{medicamento.nombre}" {estado} para {paciente.get_display_nombre()}',
        paciente=paciente,
        medicamento=medicamento,
    )
    messages.success(request, f"Recordatorio '{medicamento.nombre}' {estado}.")
    return redirect("detalle_paciente", paciente_id=paciente_id)


@login_required
def eliminar_medicamento_view(request: HttpRequest, paciente_id: int, medicamento_id: int) -> HttpResponse:
    """Vista para confirmar y eliminar un medicamento."""
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    medicamento = get_object_or_404(Medicamento, id=medicamento_id, paciente=paciente)

    if request.method == "POST":
        nombre_med = medicamento.nombre
        medicamento.delete()
        NotificacionService.crear_notificacion_sistema(
            usuario=request.user,
            titulo=f'Medicamento "{nombre_med}" eliminado para {paciente.get_display_nombre()}',
            paciente=paciente,
        )
        messages.success(request, f"Medicamento '{nombre_med}' eliminado correctamente.")
        return redirect("detalle_paciente", paciente_id=paciente_id)

    context = {
        "paciente": paciente,
        "medicamento": medicamento,
    }
    return render(request, "medicamentos/eliminar_medicamento.html", context)
