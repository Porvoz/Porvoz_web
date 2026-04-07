from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Paciente, Enfermedad
from .services import PacienteService
from apps.core.models import Perfil
from apps.dashboard.services import DashboardService
from apps.llamadas.models import Llamada
from apps.notificaciones.services import NotificacionService
from apps.shared.services import TelefonoService
from apps.usuarios.services.planes_service import PlanService


@login_required
def agregar_paciente_view(request: HttpRequest) -> HttpResponse:
    """Vista para agregar un paciente (puede ser el usuario mismo o otra persona)."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        phone_country = request.POST.get("phone_country", "+57").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        telefono = TelefonoService.formatear_completo(phone_country, phone_number)
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip()
        sexo = request.POST.get("sexo", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        notas = request.POST.get("notas", "").strip()
        parentesco = request.POST.get("parentesco", "").strip()
        timezone_str = (
            request.POST.get("timezone", "America/Bogota").strip() or "America/Bogota"
        )
        condiciones = [
            c.strip() for c in request.POST.getlist("condicion") if c and c.strip()
        ]
        es_usuario_mismo = request.POST.get("es_usuario_mismo") == "true"
        foto = request.FILES.get("foto")

        puede, error_plan = PlanService.puede_agregar_paciente(request.user)
        if not puede:
            messages.error(request, error_plan)
        elif not nombre or not telefono:
            messages.error(request, "El nombre y teléfono son obligatorios.")
        elif PacienteService.verificar_telefono_existente(request.user, telefono):
            messages.error(request, "Ya existe un paciente con ese número de teléfono.")
        else:
            # Si no se marcó explícitamente, verificar si el teléfono coincide con el del usuario
            if not es_usuario_mismo and perfil.phone:
                es_usuario_mismo = PacienteService.es_telefono_usuario_mismo(
                    perfil.phone, telefono
                )

            # Crear paciente usando service
            paciente = PacienteService.crear_paciente(
                usuario=request.user,
                nombre=nombre,
                telefono=telefono,
                fecha_nacimiento=fecha_nacimiento or None,
                sexo=sexo if sexo in dict(Paciente.SEXO_CHOICES) else "",
                parentesco=parentesco,
                descripcion=descripcion,
                notas=notas,
                timezone=timezone_str,
                es_usuario_mismo=es_usuario_mismo,
            )

            # Copiar foto del perfil si es el usuario mismo y tiene foto
            if es_usuario_mismo:
                PacienteService.copiar_foto_perfil_a_paciente(paciente, perfil)

            # Asignar foto si se subió directamente
            if foto:
                paciente.foto = foto
                paciente.save()

            # Crear condiciones si se indicaron
            for nombre_condicion in condiciones:
                PacienteService.crear_enfermedad(paciente, nombre_condicion)

            NotificacionService.crear_notificacion_sistema(
                usuario=request.user,
                titulo=f'Paciente "{paciente.get_display_nombre()}" agregado',
                paciente=paciente,
            )
            messages.success(request, f"Paciente '{nombre}' agregado correctamente.")
            return redirect("listar_pacientes")

    # Verificar si ya existe un paciente que sea el usuario mismo
    ya_existe_paciente_mismo = Paciente.objects.filter(
        usuario=request.user, es_usuario_mismo=True, activo=True
    ).exists()

    # Pre-llenar datos si es "agregarme a mí"
    prefill = request.GET.get("prefill") == "me"

    # Parsear teléfono para prefill
    prefill_phone_data = TelefonoService.prefill_desde_perfil(
        perfil.phone if prefill else None
    )
    prefill_phone_country = prefill_phone_data["pais"]
    prefill_telefono = prefill_phone_data["numero"]

    context = {
        "perfil": perfil,
        "prefill": prefill,
        "ya_existe_paciente_mismo": ya_existe_paciente_mismo,
        "prefill_nombre": (
            f"{request.user.first_name} {request.user.last_name}".strip()
            if prefill
            else ""
        ),
        "prefill_telefono": prefill_telefono,
        "sexo_choices": Paciente.SEXO_CHOICES,
        "prefill_phone_country": prefill_phone_country,
        "prefill_fecha_nacimiento": (
            perfil.date_of_birth.strftime("%Y-%m-%d")
            if prefill and perfil.date_of_birth
            else ""
        ),
        "prefill_descripcion": (
            f"Paciente autogestionado. {perfil.city or ''}".strip() if prefill else ""
        ),
        "prefill_foto_url": (
            perfil.profile_image.url if prefill and perfil.profile_image else ""
        ),
    }
    return render(request, "pacientes/agregar_paciente.html", context)


@login_required
def editar_paciente_view(request: HttpRequest, paciente_id: int) -> HttpResponse:
    """Vista para editar un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)

    if request.method == "POST":
        descripcion = request.POST.get("descripcion", "").strip()
        notas = request.POST.get("notas", "").strip()

        # Si es autogestionado: se permiten sexo, fecha nacimiento, descripción y notas
        condiciones = [
            c.strip() for c in request.POST.getlist("condicion") if c and c.strip()
        ]

        timezone_str = (
            request.POST.get("timezone", "America/Bogota").strip() or "America/Bogota"
        )

        if paciente.es_usuario_mismo:
            sexo = request.POST.get("sexo", "").strip()
            fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip() or None
            paciente.sexo = sexo if sexo in dict(Paciente.SEXO_CHOICES) else ""
            paciente.fecha_nacimiento = fecha_nacimiento
            paciente.descripcion = descripcion
            paciente.notas = notas
            paciente.timezone = timezone_str
            try:
                paciente.save()
                PacienteService.reemplazar_enfermedades(paciente, condiciones)
                NotificacionService.crear_notificacion_sistema(
                    usuario=request.user,
                    titulo=f'Información de "{paciente.get_display_nombre()}" actualizada',
                    mensaje="Datos personales (sexo, fecha nacimiento, descripción, notas).",
                    paciente=paciente,
                )
                messages.success(request, "Datos actualizados correctamente.")
                return redirect("editar_paciente", paciente_id=paciente.id)
            except Exception as e:
                messages.error(request, f"Error al actualizar: {str(e)}")
        else:
            nombre = request.POST.get("nombre", "").strip()
            phone_country = request.POST.get("phone_country", "+57").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            telefono = TelefonoService.formatear_completo(phone_country, phone_number)
            fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip() or None
            sexo = request.POST.get("sexo", "").strip()
            parentesco = request.POST.get("parentesco", "").strip()

            if not nombre or not telefono:
                messages.error(request, "El nombre y teléfono son obligatorios.")
            else:
                paciente_existente = (
                    Paciente.objects.filter(
                        usuario=request.user, telefono=telefono, activo=True
                    )
                    .exclude(id=paciente.id)
                    .first()
                )

                if paciente_existente:
                    messages.error(
                        request,
                        f"Ya existe otro paciente con el teléfono {telefono}. "
                        "Por favor, usa un número diferente.",
                    )
                else:
                    paciente.nombre = nombre
                    paciente.telefono = telefono
                    paciente.fecha_nacimiento = fecha_nacimiento
                    paciente.sexo = sexo if sexo in dict(Paciente.SEXO_CHOICES) else ""
                    paciente.parentesco = parentesco
                    paciente.descripcion = descripcion
                    paciente.notas = notas
                    paciente.timezone = timezone_str

                    foto = request.FILES.get("foto")
                    if foto:
                        paciente.foto = foto

                try:
                    paciente.save()
                    PacienteService.reemplazar_enfermedades(paciente, condiciones)
                    NotificacionService.crear_notificacion_sistema(
                        usuario=request.user,
                        titulo=f'Paciente "{paciente.get_display_nombre()}" actualizado',
                        mensaje="Datos del paciente modificados.",
                        paciente=paciente,
                    )
                    messages.success(request, "Paciente actualizado correctamente.")
                    return redirect("editar_paciente", paciente_id=paciente.id)
                except Exception as e:
                    messages.error(
                        request, f"Error al actualizar el paciente: {str(e)}"
                    )

    # Parsear teléfono para mostrar en el formulario
    tel_parsed = TelefonoService.parsear_telefono(paciente.telefono)
    telefono_pais = tel_parsed.pais
    telefono_numero = tel_parsed.numero

    context = {
        "perfil": perfil,
        "paciente": paciente,
        "telefono_pais": telefono_pais,
        "telefono_numero": telefono_numero,
        "sexo_choices": Paciente.SEXO_CHOICES,
    }
    return render(request, "pacientes/editar_paciente.html", context)


@login_required
def eliminar_paciente_view(request: HttpRequest, paciente_id: int) -> HttpResponse:
    """Vista para eliminar un paciente."""
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)

    if request.method == "POST":
        confirm_name = request.POST.get("confirm_name", "").strip()
        nombre_mostrado = paciente.get_display_nombre()
        acepta = confirm_name == paciente.nombre or confirm_name == nombre_mostrado
        if not acepta:
            messages.error(
                request,
                f"El nombre no coincide. Debes escribir exactamente: {nombre_mostrado}",
            )
        else:
            NotificacionService.crear_notificacion_sistema(
                usuario=request.user,
                titulo=f'Paciente "{nombre_mostrado}" eliminado',
            )
            paciente.delete()
            messages.success(
                request, f"Paciente '{nombre_mostrado}' eliminado correctamente."
            )
            return redirect("listar_pacientes")

    context = {
        "paciente": paciente,
    }
    return render(request, "pacientes/eliminar_paciente.html", context)


@login_required
def detalle_paciente_view(request: HttpRequest, paciente_id: int) -> HttpResponse:
    """Vista de detalle del paciente: info arriba y bloques de medicamentos/recordatorios abajo."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    context = {
        "perfil": perfil,
        "paciente": paciente,
    }
    return render(request, "pacientes/detalle_paciente.html", context)


@login_required
def historial_llamadas_paciente_view(
    request: HttpRequest, paciente_id: int
) -> HttpResponse:
    """Historial de llamadas automáticas del paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    medicamento_id = request.GET.get("medicamento", "")
    llamadas = (
        Llamada.objects.filter(paciente=paciente, usuario=request.user)
        .select_related("medicamento")
        .prefetch_related("respuesta")
        .order_by("-fecha_programada")
    )
    if medicamento_id:
        llamadas = llamadas.filter(medicamento_id=medicamento_id)

    medicamentos = paciente.medicamentos.order_by("nombre")
    context = {
        "perfil": perfil,
        "paciente": paciente,
        "llamadas": llamadas,
        "medicamentos": medicamentos,
        "medicamento_filtro": medicamento_id,
    }
    return render(request, "pacientes/historial_llamadas_paciente.html", context)


@login_required
def agregar_enfermedad_view(request: HttpRequest, paciente_id: int) -> HttpResponse:
    """Vista para agregar una enfermedad a un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        diagnostico_fecha_str = request.POST.get("diagnostico_fecha", "").strip()

        if not nombre:
            messages.error(request, "El nombre de la enfermedad es obligatorio.")
        else:
            diagnostico_fecha, error = PacienteService.parsear_fecha_diagnostico(
                diagnostico_fecha_str
            )
            if error:
                messages.error(request, error)
                return render(
                    request,
                    "pacientes/agregar_enfermedad.html",
                    {"perfil": perfil, "paciente": paciente},
                )
            PacienteService.crear_enfermedad(paciente, nombre, descripcion, diagnostico_fecha)
            NotificacionService.crear_notificacion_sistema(
                usuario=request.user,
                titulo=f'Condición "{nombre}" agregada para {paciente.get_display_nombre()}',
                paciente=paciente,
            )
            messages.success(request, f"Enfermedad '{nombre}' agregada correctamente.")
            return redirect("editar_paciente", paciente_id=paciente.id)

    context = {
        "perfil": perfil,
        "paciente": paciente,
    }
    return render(request, "pacientes/agregar_enfermedad.html", context)


@login_required
def editar_enfermedad_view(
    request: HttpRequest, paciente_id: int, enfermedad_id: int
) -> HttpResponse:
    """Vista para editar una condición/enfermedad de un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    enfermedad = get_object_or_404(Enfermedad, id=enfermedad_id, paciente=paciente)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        diagnostico_fecha_str = request.POST.get("diagnostico_fecha", "").strip()

        if not nombre:
            messages.error(request, "El nombre de la condición es obligatorio.")
        else:
            diagnostico_fecha, error = PacienteService.parsear_fecha_diagnostico(
                diagnostico_fecha_str
            )
            if error:
                messages.error(request, error)
                return render(
                    request,
                    "pacientes/editar_enfermedad.html",
                    {"perfil": perfil, "paciente": paciente, "enfermedad": enfermedad},
                )
            enfermedad.nombre = nombre
            enfermedad.descripcion = descripcion
            enfermedad.diagnostico_fecha = diagnostico_fecha
            enfermedad.save()
            NotificacionService.crear_notificacion_sistema(
                usuario=request.user,
                titulo=f'Condición "{nombre}" actualizada para {paciente.get_display_nombre()}',
                paciente=paciente,
            )
            messages.success(
                request, f"Condición '{nombre}' actualizada correctamente."
            )
            return redirect("editar_paciente", paciente_id=paciente.id)

    context = {
        "perfil": perfil,
        "paciente": paciente,
        "enfermedad": enfermedad,
    }
    return render(request, "pacientes/editar_enfermedad.html", context)


@login_required
def listar_pacientes_view(request: HttpRequest) -> HttpResponse:
    """Vista para listar todos los pacientes del usuario."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    ordenar = request.GET.get("ordenar", "recientes")

    # Delegar ordenamiento a DashboardService (elimina duplicación de lógica)
    pacientes = DashboardService.obtener_pacientes(request.user, ordenar)

    # Aplicar búsqueda si se proporcionó
    buscar = request.GET.get("buscar", "").strip()
    if buscar:
        pacientes = PacienteService.buscar_pacientes(pacientes, buscar)

    opciones_ordenar = [
        ("recientes", "Más recientes"),
        ("nombre_asc", "Nombre A-Z"),
        ("nombre_desc", "Nombre Z-A"),
        ("edad_desc", "Mayores primero"),
        ("edad_asc", "Menores primero"),
        ("condicion", "Por condición"),
        ("medicamentos", "Más medicamentos"),
        ("inicio", "Inicio tratamiento"),
    ]
    context = {
        "perfil": perfil,
        "pacientes": pacientes,
        "buscar": buscar,
        "ordenar_actual": ordenar,
        "opciones_ordenar": opciones_ordenar,
    }
    return render(request, "pacientes/listar_pacientes.html", context)
