from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.models import Perfil
from apps.llamadas.services.llamada_service import LlamadaService
from apps.notificaciones.services import NotificacionService
from apps.pacientes.models import Paciente
from apps.usuarios.services.planes_service import PlanService

from .models import Medicamento
from .services import MedicamentoService

_TIMEZONES_VALIDAS = {
    "America/Bogota", "America/Mexico_City", "America/Cancun", "America/Lima",
    "America/Guayaquil", "America/Santiago", "America/Buenos_Aires",
    "America/Caracas", "America/La_Paz", "America/Asuncion", "America/Montevideo",
    "America/New_York", "America/Chicago", "America/Los_Angeles",
    "Europe/Madrid", "UTC",
}

def _guardar_timezone_paciente(request: HttpRequest, paciente: Paciente) -> None:
    """Actualiza la zona horaria del paciente si viene en el POST y es válida."""
    tz_str = request.POST.get("timezone", "").strip()
    if not tz_str or tz_str not in _TIMEZONES_VALIDAS:
        return
    if paciente.timezone == tz_str:
        return
    try:
        ZoneInfo(tz_str)
        paciente.timezone = tz_str
        paciente.save(update_fields=["timezone"])
    except (ZoneInfoNotFoundError, Exception):
        pass


def _extraer_campos_medicamento(request: HttpRequest) -> dict:
    """Extrae y limpia los campos del formulario de medicamento."""
    return {
        "nombre": request.POST.get("nombre", "").strip(),
        "dosis": request.POST.get("dosis", "").strip(),
        "frecuencia_tipo": request.POST.get(
            "frecuencia_tipo", Medicamento.FRECUENCIA_HORARIO
        ),
        "horarios_raw": [
            h.strip() for h in request.POST.getlist("horario") if h and h.strip()
        ],
        "cada_x_horas": request.POST.get("cada_x_horas", "").strip(),
        "hora_inicio": request.POST.get("hora_inicio", "").strip(),
        "fecha_inicio_str": request.POST.get("fecha_inicio_tratamiento", "").strip(),
        "duracion_tipo": request.POST.get("duracion_tipo", "indefinido"),
        "duracion_dias_str": request.POST.get("duracion_dias", "").strip(),
        "instrucciones_llamada": request.POST.get("instrucciones_llamada", "").strip(),
        "minutos_antes_str": request.POST.get("minutos_antes_llamada", "0").strip(),
        "max_reintentos_str": request.POST.get("max_reintentos", "1").strip(),
        "minutos_reintentos_str": request.POST.get("minutos_entre_reintentos", "30").strip(),
    }


def _validar_campos_medicamento(campos: dict) -> str | None:
    """Valida los campos del medicamento. Retorna mensaje de error o None."""
    if not campos["nombre"] or not campos["dosis"]:
        return "El nombre y la dosis son obligatorios."
    if (
        campos["frecuencia_tipo"] == Medicamento.FRECUENCIA_HORARIO
        and not campos["horarios_raw"]
    ):
        return "Debes especificar al menos un horario de toma."
    if campos["frecuencia_tipo"] == Medicamento.FRECUENCIA_CADA_X_HORAS and (
        not campos["cada_x_horas"] or not campos["hora_inicio"]
    ):
        return "Debes especificar cada cuántas horas y la hora de inicio."
    d = campos["duracion_dias_str"]
    if campos["duracion_tipo"] == "dias" and (not d or not d.isdigit() or int(d) < 1):
        return "Indica cuántos días de tratamiento (número mayor a 0)."
    return None


def _campos_a_kwargs(campos: dict) -> dict:
    """Convierte los campos extraídos a kwargs para el servicio."""
    d = campos["duracion_dias_str"]
    return {
        "nombre": campos["nombre"],
        "dosis": campos["dosis"],
        "frecuencia_tipo": campos["frecuencia_tipo"],
        "horarios": campos["horarios_raw"],
        "cada_x_horas": int(campos["cada_x_horas"]) if campos["cada_x_horas"] else None,
        "hora_inicio": campos["hora_inicio"] or None,
        "fecha_inicio": campos["fecha_inicio_str"],
        "duracion_dias": int(d) if campos["duracion_tipo"] == "dias" and d else None,
        "instrucciones_llamada": campos["instrucciones_llamada"],
        "minutos_antes": (
            min(15, max(0, int(campos["minutos_antes_str"])))
            if campos["minutos_antes_str"].isdigit()
            else 0
        ),
        "max_reintentos": (
            min(3, max(0, int(campos["max_reintentos_str"])))
            if campos["max_reintentos_str"].isdigit()
            else 1
        ),
        "minutos_entre_reintentos": (
            min(10, max(5, int(campos["minutos_reintentos_str"])))
            if campos["minutos_reintentos_str"].isdigit()
            else 10
        ),
    }


@login_required
def agregar_medicamento_view(request: HttpRequest, paciente_id: int) -> HttpResponse:
    """Vista para agregar un medicamento a un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)

    if request.method == "POST":
        puede, error_plan = PlanService.puede_agregar_medicamento(request.user, paciente)
        if not puede:
            messages.error(request, error_plan)
            return redirect("detalle_paciente", paciente_id=paciente.id)
        campos = _extraer_campos_medicamento(request)
        error = _validar_campos_medicamento(campos)
        if error:
            messages.error(request, error)
        else:
            try:
                _guardar_timezone_paciente(request, paciente)
                medicamento = MedicamentoService.crear_medicamento(
                    paciente=paciente, **_campos_a_kwargs(campos)
                )
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, "medicamentos/agregar_medicamento.html", {"perfil": perfil, "paciente": paciente})
            LlamadaService.programar_llamadas_medicamento(medicamento, request.user)
            nombre_pac = paciente.get_display_nombre()
            titulo = f'Medicamento "{campos["nombre"]}" agregado para {nombre_pac}'
            NotificacionService.crear_notificacion_sistema(
                usuario=request.user,
                titulo=titulo,
                paciente=paciente,
                medicamento=medicamento,
            )
            messages.success(
                request, f"Medicamento '{campos['nombre']}' agregado correctamente."
            )
            return redirect("detalle_paciente", paciente_id=paciente.id)

    context = {"perfil": perfil, "paciente": paciente}
    return render(request, "medicamentos/agregar_medicamento.html", context)


@login_required
def editar_medicamento_view(
    request: HttpRequest, paciente_id: int, medicamento_id: int
) -> HttpResponse:
    """Vista para editar un medicamento de un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    medicamento = get_object_or_404(Medicamento, id=medicamento_id, paciente=paciente)

    if request.method == "POST":
        campos = _extraer_campos_medicamento(request)
        error = _validar_campos_medicamento(campos)
        if error:
            messages.error(request, error)
        else:
            _guardar_timezone_paciente(request, paciente)
            MedicamentoService.actualizar_medicamento(
                medicamento=medicamento, **_campos_a_kwargs(campos)
            )
            LlamadaService.programar_llamadas_medicamento(medicamento, request.user)
            nombre_pac = paciente.get_display_nombre()
            titulo = f'Medicamento "{campos["nombre"]}" actualizado para {nombre_pac}'
            NotificacionService.crear_notificacion_sistema(
                usuario=request.user,
                titulo=titulo,
                paciente=paciente,
                medicamento=medicamento,
            )
            messages.success(
                request, f"Medicamento '{campos['nombre']}' actualizado correctamente."
            )
            return redirect("detalle_paciente", paciente_id=paciente.id)

    context = {"perfil": perfil, "paciente": paciente, "medicamento": medicamento}
    return render(request, "medicamentos/editar_medicamento.html", context)


@login_required
def toggle_medicamento_view(
    request: HttpRequest, paciente_id: int, medicamento_id: int
) -> HttpResponse:
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
def eliminar_medicamento_view(
    request: HttpRequest, paciente_id: int, medicamento_id: int
) -> HttpResponse:
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
        messages.success(
            request, f"Medicamento '{nombre_med}' eliminado correctamente."
        )
        return redirect("detalle_paciente", paciente_id=paciente_id)

    context = {"paciente": paciente, "medicamento": medicamento}
    return render(request, "medicamentos/eliminar_medicamento.html", context)

