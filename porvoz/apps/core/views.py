from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Perfil


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard_router")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard_router")
        messages.error(request, "Credenciales inválidas.")

    return render(request, "core/login.html")


def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard_router")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        phone_country = request.POST.get("phone_country", "+57").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        document_type = request.POST.get("document_type", "").strip()
        document_number = request.POST.get("document_number", "").strip()
        date_of_birth = request.POST.get("date_of_birth", "").strip()
        city = request.POST.get("city", "").strip()
        emergency_contact_name = request.POST.get("emergency_contact_name", "").strip()
        emergency_contact_phone_country = request.POST.get("emergency_contact_phone_country", "+57").strip()
        emergency_contact_phone_number = request.POST.get("emergency_contact_phone_number", "").strip()

        if not username or not email or not password or not first_name or not last_name:
            messages.error(request, "Todos los campos son obligatorios.")
        elif password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
        elif date_of_birth:
            # Validar que el usuario tenga más de 10 años
            try:
                birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                if age < 10:
                    messages.error(request, "Debes tener al menos 10 años para registrarte.")
                    return render(request, "core/register.html")
            except ValueError:
                messages.error(request, "Fecha de nacimiento inválida.")
                return render(request, "core/register.html")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save(update_fields=["first_name", "last_name"])

            full_phone = f"{phone_country} {phone_number}".strip()
            emergency_phone = f"{emergency_contact_phone_country} {emergency_contact_phone_number}".strip()
            Perfil.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                phone=full_phone,
                document_type=document_type,
                document_number=document_number,
                date_of_birth=date_of_birth or None,
                city=city,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_phone=emergency_phone,
                profile_completed=True,
            )
            messages.success(request, "Cuenta creada. Inicia sesión para continuar.")
            return redirect("login")

    return render(request, "core/register.html")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")


@login_required
def dashboard_router(request: HttpRequest) -> HttpResponse:
    """Redirige al dashboard unificado."""
    return redirect("dashboard")


@login_required
def complete_profile_view(request: HttpRequest) -> HttpResponse:
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    editando = request.GET.get("edit") == "1"
    tab_activo = request.GET.get("tab", "perfil")  # 'perfil' o 'planes'

    # Manejar cambio de plan
    if request.method == "POST" and request.POST.get("action") == "cambiar_plan":
        nuevo_plan = request.POST.get("plan", "").strip()
        if nuevo_plan in [Perfil.PLAN_FREEMIUM, Perfil.PLAN_GROWTH, Perfil.PLAN_MULTI_BUSINESS]:
            perfil.plan = nuevo_plan
            perfil.save()
            messages.success(request, f"Plan actualizado a {perfil.get_plan_display()}.")
            return redirect(f"{reverse('edit_profile')}?tab=planes")
        else:
            messages.error(request, "Plan inválido.")
            return redirect(f"{reverse('edit_profile')}?tab=planes")

    # Manejar actualización de perfil
    if request.method == "POST" and request.POST.get("action") != "cambiar_plan":
        perfil.first_name = request.POST.get("first_name", "").strip()
        perfil.last_name = request.POST.get("last_name", "").strip()
        perfil.city = request.POST.get("city", "").strip()
        phone_country = request.POST.get("phone_country", "+57").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        perfil.phone = f"{phone_country} {phone_number}".strip()
        perfil.document_type = request.POST.get("document_type", "").strip()
        perfil.document_number = request.POST.get("document_number", "").strip()
        date_of_birth_str = request.POST.get("date_of_birth", "").strip()
        
        # Validar edad mínima de 10 años
        if date_of_birth_str:
            try:
                birth_date = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                if age < 10:
                    messages.error(request, "Debes tener al menos 10 años para usar este servicio.")
                    return redirect(f"{reverse('edit_profile')}?tab=perfil&edit=1")
                perfil.date_of_birth = birth_date
            except ValueError:
                messages.error(request, "Fecha de nacimiento inválida.")
                return redirect(f"{reverse('edit_profile')}?tab=perfil&edit=1")
        else:
            perfil.date_of_birth = None
        
        perfil.emergency_contact_name = request.POST.get("emergency_contact_name", "").strip()
        emergency_country = request.POST.get("emergency_contact_phone_country", "+57").strip()
        emergency_number = request.POST.get("emergency_contact_phone_number", "").strip()
        perfil.emergency_contact_phone = f"{emergency_country} {emergency_number}".strip()
        profile_image = request.FILES.get("profile_image")
        if profile_image:
            perfil.profile_image = profile_image
        perfil.profile_completed = True
        perfil.save()

        request.user.first_name = perfil.first_name or request.user.first_name
        request.user.last_name = perfil.last_name or request.user.last_name
        request.user.save()

        messages.success(request, "Perfil actualizado correctamente.")
        return redirect(f"{reverse('edit_profile')}?tab=perfil")

    # Usar datos del perfil, o del User si el perfil no los tiene
    first_name = perfil.first_name or request.user.first_name or ""
    last_name = perfil.last_name or request.user.last_name or ""
    
    # Parsear teléfonos para mostrar en el formulario
    phone_country = "+57"
    phone_number = ""
    if perfil.phone:
        phone_clean = perfil.phone.strip()
        if " " in phone_clean:
            parts = phone_clean.split(" ", 1)
            phone_country = parts[0] if parts[0].startswith("+") else f"+{parts[0]}"
            phone_number = parts[1].strip()
        elif phone_clean.startswith("+"):
            if phone_clean.startswith("+57"):
                phone_country = "+57"
                phone_number = phone_clean[3:].strip()
            elif phone_clean.startswith("+1"):
                phone_country = "+1"
                phone_number = phone_clean[2:].strip()
            elif phone_clean.startswith("+34"):
                phone_country = "+34"
                phone_number = phone_clean[3:].strip()
            elif phone_clean.startswith("+52"):
                phone_country = "+52"
                phone_number = phone_clean[3:].strip()
            else:
                phone_country = "+57"
                phone_number = phone_clean[1:].strip()
        else:
            phone_country = "+57"
            phone_number = phone_clean

    emergency_phone_country = "+57"
    emergency_phone_number = ""
    if perfil.emergency_contact_phone:
        emergency_clean = perfil.emergency_contact_phone.strip()
        if " " in emergency_clean:
            parts = emergency_clean.split(" ", 1)
            emergency_phone_country = parts[0] if parts[0].startswith("+") else f"+{parts[0]}"
            emergency_phone_number = parts[1].strip()
        elif emergency_clean.startswith("+"):
            if emergency_clean.startswith("+57"):
                emergency_phone_country = "+57"
                emergency_phone_number = emergency_clean[3:].strip()
            elif emergency_clean.startswith("+1"):
                emergency_phone_country = "+1"
                emergency_phone_number = emergency_clean[2:].strip()
            elif emergency_clean.startswith("+34"):
                emergency_phone_country = "+34"
                emergency_phone_number = emergency_clean[3:].strip()
            elif emergency_clean.startswith("+52"):
                emergency_phone_country = "+52"
                emergency_phone_number = emergency_clean[3:].strip()
            else:
                emergency_phone_country = "+57"
                emergency_phone_number = emergency_clean[1:].strip()
        else:
            emergency_phone_country = "+57"
            emergency_phone_number = emergency_clean

    # Preparar datos de planes
    planes_data = {
        Perfil.PLAN_FREEMIUM: {
            "nombre": "Freemium",
            "tagline": "Accede a recordatorios de medicamentos completamente gratis",
            "precio": "$0",
            "precio_cop": None,
            "precio_mensual": 0,
            "destacado": False,
            "caracteristicas": [
                "1 Cuidador",
                "Hasta 2 pacientes",
                "Hasta 5 medicamentos",
                "30 llamadas automatizadas/mes",
                "Recordatorios básicos",
                "Dashboard de seguimiento",
                "Historial de 3 meses",
                "Llamadas con IA en español",
            ],
            "boton_texto": "Usar gratis",
            "boton_estilo": "border-blue-800 text-blue-800 hover:bg-blue-100",
        },
        Perfil.PLAN_GROWTH: {
            "nombre": "Growth Plan",
            "tagline": "Ideal para familias que necesitan seguimiento completo",
            "precio": "$19",
            "precio_cop": "59.900",
            "precio_mensual": 19,
            "destacado": True,
            "ahorro": "Ahorra en el año",
            "caracteristicas": [
                "1 Cuidador",
                "Pacientes ilimitados",
                "Medicamentos ilimitados",
                "Llamadas ilimitadas",
                "Recordatorios avanzados",
                "Dashboard completo",
                "Historial completo",
                "Llamadas con IA personalizadas",
                "Alertas de adherencia",
                "Reportes de seguimiento",
            ],
            "boton_texto": "Hazte Premium",
            "boton_estilo": "bg-blue-800 text-white hover:bg-blue-900",
        },
        Perfil.PLAN_MULTI_BUSINESS: {
            "nombre": "Multi-cuidador",
            "tagline": "Para instituciones y múltiples cuidadores",
            "precio": "+ $15",
            "precio_cop": "79.900",
            "precio_mensual": 15,
            "destacado": False,
            "caracteristicas": [
                "Todo lo del Growth Plan:",
                "2-10 cuidadores",
                "79.900 COP por cuidador adicional",
                "Gestión centralizada",
                "Reportes consolidados",
                "Soporte prioritario",
            ],
            "boton_texto": "Contactar",
            "boton_estilo": "border-blue-800 text-blue-800 hover:bg-blue-100",
        },
    }
    
    planes = [
        {**planes_data[Perfil.PLAN_FREEMIUM], "plan_key": Perfil.PLAN_FREEMIUM},
        {**planes_data[Perfil.PLAN_GROWTH], "plan_key": Perfil.PLAN_GROWTH},
        {**planes_data[Perfil.PLAN_MULTI_BUSINESS], "plan_key": Perfil.PLAN_MULTI_BUSINESS},
    ]
    
    for plan in planes:
        plan["es_plan_actual"] = perfil.plan == plan["plan_key"]

    context = {
        "perfil": perfil,
        "first_name": first_name,
        "last_name": last_name,
        "phone_country": phone_country,
        "phone_number": phone_number,
        "emergency_phone_country": emergency_phone_country,
        "emergency_phone_number": emergency_phone_number,
        "editando": editando,
        "tab_activo": tab_activo,
        "planes": planes,
    }
    return render(request, "core/edit_profile.html", context)


@login_required
def dashboard_unificado(request: HttpRequest) -> HttpResponse:
    """Dashboard con estadísticas y resumen del usuario."""
    from apps.pacientes.models import Paciente
    from apps.medicamentos.models import Medicamento
    from datetime import datetime, timedelta
    
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    
    # Obtener pacientes (select_related para get_display_* en templates)
    pacientes = Paciente.objects.filter(
        usuario=request.user,
        activo=True
    ).select_related("usuario", "usuario__perfil").prefetch_related('medicamentos', 'enfermedades').order_by("-es_usuario_mismo", "-creado_en")
    
    # Calcular estadísticas
    total_medicamentos = Medicamento.objects.filter(
        paciente__usuario=request.user,
        activo=True
    ).count()
    
    # Próximos recordatorios: medicamentos del usuario con horario fijo, ordenados por hora (máx. 5)
    medicamentos_con_horario = Medicamento.objects.filter(
        paciente__usuario=request.user,
        activo=True,
        frecuencia_tipo=Medicamento.FRECUENCIA_HORARIO,
        horario__isnull=False
    ).select_related('paciente').order_by('horario')[:5]
    
    hoy = datetime.now().date()
    proximos_recordatorios = [
        {'medicamento': med, 'horario': med.horario, 'fecha': hoy}
        for med in medicamentos_con_horario
    ]
    
    # Actividad reciente: últimas acciones (pacientes y medicamentos agregados) ordenadas por fecha
    actividad_reciente = []
    for p in Paciente.objects.filter(usuario=request.user, activo=True).select_related("usuario", "usuario__perfil").order_by('-creado_en')[:5]:
        actividad_reciente.append({'icono': 'person-plus', 'descripcion': f'Paciente "{p.get_display_nombre()}" agregado', 'fecha': p.creado_en})
    for m in Medicamento.objects.filter(paciente__usuario=request.user, activo=True).select_related('paciente', 'paciente__usuario', 'paciente__usuario__perfil').order_by('-creado_en')[:10]:
        actividad_reciente.append({'icono': 'capsule', 'descripcion': f'Medicamento "{m.nombre}" agregado para {m.paciente.get_display_nombre()}', 'fecha': m.creado_en})
    actividad_reciente.sort(key=lambda x: x['fecha'], reverse=True)
    actividad_reciente = actividad_reciente[:5]
    
    context = {
        "perfil": perfil,
        "pacientes": pacientes,
        "total_medicamentos": total_medicamentos,
        "llamadas_hoy": 0,  # Placeholder
        "adherencia": 85,  # Placeholder
        "proximos_recordatorios": proximos_recordatorios[:5],
        "actividad_reciente": actividad_reciente[:5],
    }
    return render(request, "core/dashboard.html", context)


@login_required
def notifications_view(request: HttpRequest) -> HttpResponse:
    """Vista para gestionar notificaciones con filtros y eliminación."""
    from apps.llamadas.models import Notificacion
    from apps.pacientes.models import Paciente
    from datetime import datetime, timedelta
    
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    
    # Manejar eliminación
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "delete_selected":
            notificacion_ids = request.POST.getlist("notificacion_ids")
            if notificacion_ids:
                Notificacion.objects.filter(
                    id__in=notificacion_ids,
                    usuario=request.user
                ).delete()
                messages.success(request, f"{len(notificacion_ids)} notificación(es) eliminada(s).")
                return redirect("notifications")
        
        elif action == "delete_single":
            notificacion_id = request.POST.get("notificacion_id")
            if notificacion_id:
                try:
                    notificacion = Notificacion.objects.get(id=notificacion_id, usuario=request.user)
                    notificacion.delete()
                    messages.success(request, "Notificación eliminada.")
                except Notificacion.DoesNotExist:
                    messages.error(request, "Notificación no encontrada.")
                return redirect("notifications")
        
        elif action == "mark_read":
            notificacion_ids = request.POST.getlist("notificacion_ids")
            if notificacion_ids:
                Notificacion.objects.filter(
                    id__in=notificacion_ids,
                    usuario=request.user
                ).update(leida=True)
                messages.success(request, f"{len(notificacion_ids)} notificación(es) marcada(s) como leída(s).")
                return redirect("notifications")
    
    # Obtener filtros
    paciente_id = request.GET.get("paciente")
    tipo = request.GET.get("tipo")
    estado = request.GET.get("estado")
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")
    solo_no_leidas = request.GET.get("solo_no_leidas") == "1"
    buscar = request.GET.get("buscar", "").strip()
    
    # Construir query
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    
    if paciente_id:
        notificaciones = notificaciones.filter(paciente_id=paciente_id)
    
    if tipo:
        notificaciones = notificaciones.filter(tipo=tipo)
    
    if estado:
        notificaciones = notificaciones.filter(estado=estado)
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
            notificaciones = notificaciones.filter(creado_en__date__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
            notificaciones = notificaciones.filter(creado_en__date__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    if solo_no_leidas:
        notificaciones = notificaciones.filter(leida=False)
    
    if buscar:
        notificaciones = notificaciones.filter(
            Q(titulo__icontains=buscar) |
            Q(mensaje__icontains=buscar)
        )
    
    notificaciones = notificaciones.select_related("paciente", "paciente__usuario", "paciente__usuario__perfil", "medicamento").order_by("-creado_en")
    
    # Obtener pacientes para el filtro (select_related para get_display_nombre)
    pacientes = Paciente.objects.filter(usuario=request.user, activo=True).select_related("usuario", "usuario__perfil").order_by("nombre")
    
    # Estadísticas
    total_notificaciones = Notificacion.objects.filter(usuario=request.user).count()
    no_leidas = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    llamadas_atendidas = Notificacion.objects.filter(
        usuario=request.user,
        tipo=Notificacion.TIPO_LLAMADA,
        estado=Notificacion.ESTADO_ATENDIDA
    ).count()
    
    context = {
        "perfil": perfil,
        "notificaciones": notificaciones,
        "pacientes": pacientes,
        "paciente_seleccionado": paciente_id,
        "tipo_seleccionado": tipo,
        "estado_seleccionado": estado,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "solo_no_leidas": solo_no_leidas,
        "buscar": buscar,
        "total_notificaciones": total_notificaciones,
        "no_leidas": no_leidas,
        "llamadas_atendidas": llamadas_atendidas,
        "tipos": Notificacion.TIPO_CHOICES,
        "estados": Notificacion.ESTADO_CHOICES,
    }
    return render(request, "core/notifications.html", context)


def plans_view(request: HttpRequest) -> HttpResponse:
    """Vista para mostrar los planes disponibles y actualizar el plan del usuario."""
    # Si el usuario está autenticado, puede cambiar de plan
    if request.user.is_authenticated:
        perfil, _ = Perfil.objects.get_or_create(user=request.user)
        
        if request.method == "POST":
            nuevo_plan = request.POST.get("plan", "").strip()
            if nuevo_plan in [Perfil.PLAN_FREEMIUM, Perfil.PLAN_GROWTH, Perfil.PLAN_MULTI_BUSINESS]:
                perfil.plan = nuevo_plan
                perfil.save()
                messages.success(request, f"Plan actualizado a {perfil.get_plan_display()}.")
                return redirect("plans")
            else:
                messages.error(request, "Plan inválido.")
        plan_actual = perfil.plan
    else:
        perfil = None
        plan_actual = None
    
    # Definir los planes con sus características (relevantes a Porvoz)
    planes_data = {
        Perfil.PLAN_FREEMIUM: {
            "nombre": "Freemium",
            "tagline": "Accede a recordatorios de medicamentos completamente gratis",
            "precio": "$0",
            "precio_cop": None,
            "precio_mensual": 0,
            "destacado": False,
            "caracteristicas": [
                "1 Cuidador",
                "Hasta 2 pacientes",
                "Hasta 5 medicamentos",
                "30 llamadas automatizadas/mes",
                "Recordatorios básicos",
                "Dashboard de seguimiento",
                "Historial de 3 meses",
                "Llamadas con IA en español",
            ],
            "boton_texto": "Usar gratis",
            "boton_estilo": "border-blue-800 text-blue-800 hover:bg-blue-100",
        },
        Perfil.PLAN_GROWTH: {
            "nombre": "Growth Plan",
            "tagline": "Ideal para familias que necesitan seguimiento completo",
            "precio": "$19",
            "precio_cop": "59.900",
            "precio_mensual": 19,
            "destacado": True,
            "ahorro": "Ahorra en el año",
            "caracteristicas": [
                "1 Cuidador",
                "Pacientes ilimitados",
                "Medicamentos ilimitados",
                "Llamadas ilimitadas",
                "Recordatorios avanzados",
                "Dashboard completo",
                "Historial completo",
                "Llamadas con IA personalizadas",
                "Alertas de adherencia",
                "Reportes de seguimiento",
            ],
            "boton_texto": "Hazte Premium",
            "boton_estilo": "bg-blue-800 text-white hover:bg-blue-900",
        },
        Perfil.PLAN_MULTI_BUSINESS: {
            "nombre": "Multi-cuidador",
            "tagline": "Para instituciones y múltiples cuidadores",
            "precio": "+ $15",
            "precio_cop": "79.900",
            "precio_mensual": 15,
            "destacado": False,
            "caracteristicas": [
                "Todo lo del Growth Plan:",
                "2-10 cuidadores",
                "79.900 COP por cuidador adicional",
                "Gestión centralizada",
                "Reportes consolidados",
                "Soporte prioritario",
            ],
            "boton_texto": "Contactar",
            "boton_estilo": "border-blue-800 text-blue-800 hover:bg-blue-100",
        },
    }
    
    # Preparar los planes en orden
    planes = [
        {**planes_data[Perfil.PLAN_FREEMIUM], "plan_key": Perfil.PLAN_FREEMIUM},
        {**planes_data[Perfil.PLAN_GROWTH], "plan_key": Perfil.PLAN_GROWTH},
        {**planes_data[Perfil.PLAN_MULTI_BUSINESS], "plan_key": Perfil.PLAN_MULTI_BUSINESS},
    ]
    
    # Marcar el plan actual (solo si está autenticado)
    for plan in planes:
        if plan_actual:
            plan["es_plan_actual"] = plan_actual == plan["plan_key"]
        else:
            plan["es_plan_actual"] = False
    
    context = {
        "perfil": perfil,
        "planes": planes,
        "plan_actual": plan_actual,
    }
    return render(request, "core/plans.html", context)




@login_required
def change_password_view(request: HttpRequest) -> HttpResponse:
    """Vista para cambiar la contraseña del usuario."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == "POST":
        old_password = request.POST.get("old_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not old_password or not new_password or not confirm_password:
            messages.error(request, "Todos los campos son obligatorios.")
        elif not request.user.check_password(old_password):
            messages.error(request, "La contraseña actual es incorrecta.")
        elif len(new_password) < 8:
            messages.error(request, "La nueva contraseña debe tener al menos 8 caracteres.")
        elif new_password != confirm_password:
            messages.error(request, "Las nuevas contraseñas no coinciden.")
        elif old_password == new_password:
            messages.error(request, "La nueva contraseña debe ser diferente a la actual.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "Contraseña actualizada correctamente. Por favor, inicia sesión nuevamente.")
            return redirect("login")

    return render(request, "core/change_password.html", {"perfil": perfil})


def reset_password_view(request: HttpRequest) -> HttpResponse:
    """Vista para solicitar recuperación de contraseña."""
    if request.user.is_authenticated:
        return redirect("dashboard_router")

    if request.method == "POST":
        username_or_email = request.POST.get("username_or_email", "").strip()
        
        if not username_or_email:
            messages.error(request, "Por favor ingresa tu usuario o correo electrónico.")
        else:
            # Buscar usuario por username o email
            from django.contrib.auth.models import User
            try:
                if "@" in username_or_email:
                    user = User.objects.get(email=username_or_email)
                else:
                    user = User.objects.get(username=username_or_email)
                
                # Aquí iría la lógica para enviar el email de recuperación
                # Por ahora solo mostramos un mensaje de éxito
                messages.success(
                    request,
                    f"Si existe una cuenta con ese usuario o correo, se ha enviado un enlace de recuperación. "
                    f"Por favor revisa tu correo electrónico. (Funcionalidad en desarrollo)"
                )
            except User.DoesNotExist:
                # Por seguridad, no revelamos si el usuario existe o no
                messages.success(
                    request,
                    "Si existe una cuenta con ese usuario o correo, se ha enviado un enlace de recuperación. "
                    "Por favor revisa tu correo electrónico. (Funcionalidad en desarrollo)"
                )

    return render(request, "core/reset_password.html")


def legal_info_view(request: HttpRequest) -> HttpResponse:
    """Vista para mostrar información legal: términos, privacidad y contacto."""
    return render(request, "core/legal_info.html")


def guide_view(request: HttpRequest) -> HttpResponse:
    """Vista para mostrar la guía rápida y preguntas frecuentes."""
    return render(request, "core/guide.html")

