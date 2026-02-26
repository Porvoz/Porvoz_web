import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .models import Paciente, Enfermedad
from apps.core.models import Perfil


@login_required
def agregar_paciente_view(request: HttpRequest) -> HttpResponse:
    """Vista para agregar un paciente (puede ser el usuario mismo o otra persona)."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        phone_country = request.POST.get("phone_country", "+57").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        telefono = f"{phone_country} {phone_number}".strip() if phone_number else ""
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        notas = request.POST.get("notas", "").strip()
        es_usuario_mismo = request.POST.get("es_usuario_mismo") == "true"
        foto = request.FILES.get("foto")
        
        if not nombre or not telefono:
            messages.error(request, "El nombre y teléfono son obligatorios.")
        elif Paciente.objects.filter(usuario=request.user, telefono=telefono, activo=True).exists():
            messages.error(request, "Ya existe un paciente con ese número de teléfono.")
        else:
            # Si no se marcó explícitamente, verificar si el teléfono coincide con el del usuario
            if not es_usuario_mismo and perfil.phone:
                telefono_normalizado = telefono.replace(" ", "").replace("-", "")
                perfil_telefono_normalizado = perfil.phone.replace(" ", "").replace("-", "")
                if perfil_telefono_normalizado.endswith(telefono_normalizado) or telefono_normalizado in perfil_telefono_normalizado:
                    es_usuario_mismo = True
            
            paciente = Paciente.objects.create(
                usuario=request.user,
                nombre=nombre,
                telefono=telefono,
                fecha_nacimiento=fecha_nacimiento or None,
                descripcion=descripcion,
                notas=notas,
                es_usuario_mismo=es_usuario_mismo,
            )
            
            # Si es el usuario mismo y tiene foto de perfil, copiarla
            if es_usuario_mismo and perfil.profile_image:
                # Copiar el archivo de imagen del perfil al paciente
                try:
                    with open(perfil.profile_image.path, 'rb') as f:
                        paciente.foto.save(
                            os.path.basename(perfil.profile_image.name),
                            File(f),
                            save=True
                        )
                except (ValueError, IOError):
                    # Si no se puede copiar, simplemente asignar la referencia
                    paciente.foto = perfil.profile_image
                    paciente.save()
            elif foto:
                paciente.foto = foto
                paciente.save()
            
            messages.success(request, f"Paciente '{nombre}' agregado correctamente.")
            return redirect("listar_pacientes")
    
    # Verificar si ya existe un paciente que sea el usuario mismo
    ya_existe_paciente_mismo = Paciente.objects.filter(
        usuario=request.user,
        es_usuario_mismo=True,
        activo=True
    ).exists()
    
    # Pre-llenar datos si es "agregarme a mí"
    prefill = request.GET.get("prefill") == "me"
    
    # Parsear teléfono para prefill
    prefill_telefono = ""
    prefill_phone_country = "+57"
    if prefill and perfil.phone:
        # Extraer código de país y número
        phone_clean = perfil.phone.strip()
        if " " in phone_clean:
            parts = phone_clean.split(" ", 1)
            prefill_phone_country = parts[0].strip()
            prefill_telefono = parts[1].strip()
        elif phone_clean.startswith("+57"):
            prefill_phone_country = "+57"
            prefill_telefono = phone_clean[3:].strip()
        elif phone_clean.startswith("+1"):
            prefill_phone_country = "+1"
            prefill_telefono = phone_clean[2:].strip()
        elif phone_clean.startswith("+34"):
            prefill_phone_country = "+34"
            prefill_telefono = phone_clean[3:].strip()
        elif phone_clean.startswith("+52"):
            prefill_phone_country = "+52"
            prefill_telefono = phone_clean[3:].strip()
        else:
            prefill_telefono = phone_clean.replace("+", "").strip()
    
    context = {
        "perfil": perfil,
        "prefill": prefill,
        "ya_existe_paciente_mismo": ya_existe_paciente_mismo,
        "prefill_nombre": f"{request.user.first_name} {request.user.last_name}".strip() if prefill else "",
        "prefill_telefono": prefill_telefono,
        "prefill_phone_country": prefill_phone_country,
        "prefill_fecha_nacimiento": perfil.date_of_birth.strftime("%Y-%m-%d") if prefill and perfil.date_of_birth else "",
        "prefill_descripcion": f"Paciente autogestionado. {perfil.city or ''}".strip() if prefill else "",
        "prefill_foto_url": perfil.profile_image.url if prefill and perfil.profile_image else "",
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

        # Si es autogestionado (el usuario mismo), solo se permiten descripción y notas
        if paciente.es_usuario_mismo:
            paciente.descripcion = descripcion
            paciente.notas = notas
            try:
                paciente.save()
                messages.success(request, "Datos actualizados correctamente.")
                return redirect("listar_pacientes")
            except Exception as e:
                messages.error(request, f"Error al actualizar: {str(e)}")
        else:
            nombre = request.POST.get("nombre", "").strip()
            phone_country = request.POST.get("phone_country", "+57").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            telefono = f"{phone_country} {phone_number}".strip() if phone_number else ""
            fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip() or None

            if not nombre or not telefono:
                messages.error(request, "El nombre y teléfono son obligatorios.")
            else:
                paciente_existente = Paciente.objects.filter(
                    usuario=request.user,
                    telefono=telefono,
                    activo=True
                ).exclude(id=paciente.id).first()

                if paciente_existente:
                    messages.error(request, f"Ya existe otro paciente con el número de teléfono {telefono}. Por favor, usa un número diferente.")
                else:
                    paciente.nombre = nombre
                    paciente.telefono = telefono
                    paciente.fecha_nacimiento = fecha_nacimiento
                    paciente.descripcion = descripcion
                    paciente.notas = notas

                    foto = request.FILES.get("foto")
                    if foto:
                        paciente.foto = foto

                    try:
                        paciente.save()
                        messages.success(request, f"Paciente '{paciente.nombre}' actualizado correctamente.")
                        return redirect("listar_pacientes")
                    except Exception as e:
                        messages.error(request, f"Error al actualizar el paciente: {str(e)}")
    
    # Parsear teléfono para mostrar en el formulario
    telefono_pais = "+57"
    telefono_numero = paciente.telefono
    if paciente.telefono:
        if paciente.telefono.startswith("+57"):
            telefono_pais = "+57"
            telefono_numero = paciente.telefono[3:].strip()
        elif paciente.telefono.startswith("+1"):
            telefono_pais = "+1"
            telefono_numero = paciente.telefono[2:].strip()
        elif paciente.telefono.startswith("+34"):
            telefono_pais = "+34"
            telefono_numero = paciente.telefono[3:].strip()
        elif paciente.telefono.startswith("+52"):
            telefono_pais = "+52"
            telefono_numero = paciente.telefono[3:].strip()
        elif " " in paciente.telefono:
            parts = paciente.telefono.split(" ", 1)
            telefono_pais = parts[0]
            telefono_numero = parts[1] if len(parts) > 1 else ""
    
    context = {
        "perfil": perfil,
        "paciente": paciente,
        "telefono_pais": telefono_pais,
        "telefono_numero": telefono_numero,
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
            messages.error(request, f"El nombre no coincide. Debes escribir exactamente: {nombre_mostrado}")
        else:
            paciente.delete()
            messages.success(request, f"Paciente '{nombre_mostrado}' eliminado correctamente.")
            return redirect("listar_pacientes")
    
    context = {
        "paciente": paciente,
    }
    return render(request, "pacientes/eliminar_paciente.html", context)


@login_required
def agregar_enfermedad_view(request: HttpRequest, paciente_id: int) -> HttpResponse:
    """Vista para agregar una enfermedad a un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        diagnostico_fecha = request.POST.get("diagnostico_fecha", "").strip()
        
        if not nombre:
            messages.error(request, "El nombre de la enfermedad es obligatorio.")
        else:
            Enfermedad.objects.create(
                paciente=paciente,
                nombre=nombre,
                descripcion=descripcion,
                diagnostico_fecha=diagnostico_fecha or None,
            )
            messages.success(request, f"Enfermedad '{nombre}' agregada correctamente.")
            return redirect("listar_pacientes")
    
    context = {
        "perfil": perfil,
        "paciente": paciente,
    }
    return render(request, "pacientes/agregar_enfermedad.html", context)


@login_required
def editar_enfermedad_view(request: HttpRequest, paciente_id: int, enfermedad_id: int) -> HttpResponse:
    """Vista para editar una condición/enfermedad de un paciente."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)
    enfermedad = get_object_or_404(Enfermedad, id=enfermedad_id, paciente=paciente)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        diagnostico_fecha = request.POST.get("diagnostico_fecha", "").strip()

        if not nombre:
            messages.error(request, "El nombre de la condición es obligatorio.")
        else:
            enfermedad.nombre = nombre
            enfermedad.descripcion = descripcion
            enfermedad.diagnostico_fecha = diagnostico_fecha or None
            enfermedad.save()
            messages.success(request, f"Condición '{nombre}' actualizada correctamente.")
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
    pacientes = Paciente.objects.filter(usuario=request.user, activo=True).select_related("usuario", "usuario__perfil").order_by("-es_usuario_mismo", "-creado_en")
    
    # Filtro de búsqueda por nombre
    buscar = request.GET.get("buscar", "").strip()
    if buscar:
        pacientes = pacientes.filter(nombre__icontains=buscar)
    
    context = {
        "perfil": perfil,
        "pacientes": pacientes,
        "buscar": buscar,
    }
    return render(request, "pacientes/listar_pacientes.html", context)
