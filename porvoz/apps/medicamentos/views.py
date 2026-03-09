from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .models import Medicamento, HorarioMedicamento
from apps.pacientes.models import Paciente
from apps.core.models import Perfil
from apps.llamadas.models import Notificacion


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
            fecha_inicio = None
            if fecha_inicio_str:
                try:
                    from datetime import datetime
                    fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
                except ValueError:
                    pass
            minutos_antes = 0
            if minutos_antes_str.isdigit():
                minutos_antes = min(120, max(0, int(minutos_antes_str)))
            horario_legacy = None
            if horarios_raw and frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO:
                try:
                    from datetime import datetime
                    horario_legacy = datetime.strptime(horarios_raw[0], "%H:%M").time()
                except ValueError:
                    pass
            medicamento = Medicamento.objects.create(
                paciente=paciente,
                nombre=nombre,
                dosis=dosis,
                frecuencia_tipo=frecuencia_tipo,
                horario=horario_legacy,
                cada_x_horas=int(cada_x_horas) if cada_x_horas else None,
                hora_inicio=hora_inicio or None,
                fecha_inicio_tratamiento=fecha_inicio,
                duracion_dias=duracion_dias,
                instrucciones_llamada=instrucciones_llamada,
                minutos_antes_llamada=minutos_antes,
            )
            for i, h in enumerate(horarios_raw):
                if frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO and h:
                    try:
                        from datetime import datetime
                        hora_obj = datetime.strptime(h, "%H:%M").time()
                        HorarioMedicamento.objects.create(medicamento=medicamento, hora=hora_obj, orden=i)
                    except ValueError:
                        pass
            Notificacion.objects.create(
                usuario=request.user,
                paciente=paciente,
                medicamento=medicamento,
                tipo=Notificacion.TIPO_SISTEMA,
                titulo=f'Medicamento "{nombre}" agregado para {paciente.get_display_nombre()}',
                mensaje="",
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
            fecha_inicio = None
            if fecha_inicio_str:
                try:
                    from datetime import datetime
                    fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
                except ValueError:
                    pass
            minutos_antes = 0
            if minutos_antes_str.isdigit():
                minutos_antes = min(120, max(0, int(minutos_antes_str)))
            horario_legacy = None
            if horarios_raw and frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO:
                try:
                    from datetime import datetime
                    horario_legacy = datetime.strptime(horarios_raw[0], "%H:%M").time()
                except ValueError:
                    pass
            medicamento.nombre = nombre
            medicamento.dosis = dosis
            medicamento.frecuencia_tipo = frecuencia_tipo
            medicamento.horario = horario_legacy
            medicamento.cada_x_horas = int(cada_x_horas) if cada_x_horas else None
            medicamento.hora_inicio = hora_inicio or None
            medicamento.fecha_inicio_tratamiento = fecha_inicio
            medicamento.duracion_dias = duracion_dias
            medicamento.instrucciones_llamada = instrucciones_llamada
            medicamento.minutos_antes_llamada = minutos_antes
            medicamento.save()
            medicamento.horarios.all().delete()
            for i, h in enumerate(horarios_raw):
                if frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO and h:
                    try:
                        from datetime import datetime
                        hora_obj = datetime.strptime(h, "%H:%M").time()
                        HorarioMedicamento.objects.create(medicamento=medicamento, hora=hora_obj, orden=i)
                    except ValueError:
                        pass
            Notificacion.objects.create(
                usuario=request.user,
                paciente=paciente,
                medicamento=medicamento,
                tipo=Notificacion.TIPO_SISTEMA,
                titulo=f'Medicamento "{nombre}" actualizado para {paciente.get_display_nombre()}',
                mensaje="",
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
    medicamento.activo = not medicamento.activo
    medicamento.save()
    estado = "activado" if medicamento.activo else "desactivado"
    Notificacion.objects.create(
        usuario=request.user,
        paciente=paciente,
        medicamento=medicamento,
        tipo=Notificacion.TIPO_SISTEMA,
        titulo=f'Recordatorio "{medicamento.nombre}" {estado} para {paciente.get_display_nombre()}',
        mensaje="",
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
        Notificacion.objects.create(
            usuario=request.user,
            paciente=paciente,
            tipo=Notificacion.TIPO_SISTEMA,
            titulo=f'Medicamento "{nombre_med}" eliminado para {paciente.get_display_nombre()}',
            mensaje="",
        )
        messages.success(request, f"Medicamento '{nombre_med}' eliminado correctamente.")
        return redirect("detalle_paciente", paciente_id=paciente_id)

    context = {
        "paciente": paciente,
        "medicamento": medicamento,
    }
    return render(request, "medicamentos/eliminar_medicamento.html", context)
