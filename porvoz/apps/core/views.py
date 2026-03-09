from datetime import date, datetime, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

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

        # Todas las validaciones pasaron: crear usuario y perfil
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])

        birth_date_obj = None
        if date_of_birth:
            try:
                birth_date_obj = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            except ValueError:
                pass

        full_phone = f"{phone_country} {phone_number}".strip()
        emergency_phone = f"{emergency_contact_phone_country} {emergency_contact_phone_number}".strip()
        plan_expiration = date.today() + timedelta(days=365)
        Perfil.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone=full_phone,
            document_type=document_type or "",
            document_number=document_number,
            date_of_birth=birth_date_obj,
            city=city,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone=emergency_phone,
            profile_completed=True,
            plan_expiration=plan_expiration,
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
            perfil.plan_expiration = date.today() + timedelta(days=365)
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

    # Planes (mismos datos que en plans_view)
    planes_data = {
        Perfil.PLAN_FREEMIUM: {
            "nombre": "Prueba",
            "tagline": "Prueba el servicio con límites.",
            "precio": "$0",
            "precio_cop": None,
            "precio_mensual": 0,
            "destacado": False,
            "caracteristicas": [
                "1 Cuidador",
                "1 paciente",
                "Hasta 3 medicamentos",
                "10 llamadas/mes",
                "Dashboard básico",
                "Historial 1 mes",
            ],
            "boton_texto": "Empezar prueba",
            "boton_estilo": "border-slate-700 text-slate-700 hover:bg-slate-50",
        },
        Perfil.PLAN_GROWTH: {
            "nombre": "Growth",
            "tagline": "Para familias. Llamadas ilimitadas.",
            "precio": "$79.900",
            "precio_cop": "79.900",
            "precio_mensual": 79900,
            "destacado": True,
            "ahorro": "Ahorra en el año",
            "caracteristicas": [
                "1 Cuidador",
                "Pacientes ilimitados",
                "Medicamentos ilimitados",
                "Llamadas ilimitadas",
                "Dashboard completo",
                "Historial 12 meses",
                "Alertas de adherencia",
                "Soporte por correo",
            ],
            "boton_texto": "Contratar Growth",
            "boton_estilo": "bg-slate-800 text-white hover:bg-slate-700",
        },
        Perfil.PLAN_MULTI_BUSINESS: {
            "nombre": "Multi-cuidador",
            "tagline": "Instituciones y equipos.",
            "precio": "$99.900",
            "precio_cop": "99.900",
            "precio_mensual": 99900,
            "destacado": False,
            "caracteristicas": [
                "Todo lo de Growth",
                "2 a 10 cuidadores",
                "99.900 COP/cuidador/mes",
                "Gestión centralizada",
                "Soporte prioritario",
            ],
            "boton_texto": "Contactar ventas",
            "boton_estilo": "border-slate-800 text-slate-800 hover:bg-slate-100",
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


def _icono_para_notificacion(notif):
    """Mapea tipo/título de notificación a icono para actividad reciente."""
    if notif.tipo == "alerta":
        return "exclamation-triangle"
    if notif.tipo == "llamada":
        return "telephone"
    if notif.tipo == "recordatorio":
        return "bell"
    # Sistema: inferir por título
    tit = notif.titulo or ""
    if "Paciente" in tit:
        return "person-plus"
    if "Medicamento" in tit:
        return "capsule"
    if "Condición" in tit:
        return "heart-pulse"
    return "info-circle"


@login_required
def dashboard_unificado(request: HttpRequest) -> HttpResponse:
    """Dashboard con estadísticas y resumen del usuario."""
    from apps.pacientes.models import Paciente
    from apps.medicamentos.models import Medicamento
    from apps.llamadas.models import Notificacion
    from datetime import datetime, timedelta
    
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    
    # Obtener pacientes con orden configurable
    ordenar = request.GET.get("ordenar", "recientes")
    base_qs = Paciente.objects.filter(usuario=request.user, activo=True).select_related(
        "usuario", "usuario__perfil"
    ).prefetch_related('medicamentos', 'enfermedades')
    if ordenar == "nombre_asc":
        pacientes = list(base_qs.order_by("nombre"))
    elif ordenar == "nombre_desc":
        pacientes = list(base_qs.order_by("-nombre"))
    elif ordenar in ("medicamentos", "inicio", "edad_asc", "edad_desc", "condicion"):
        base_list = list(base_qs)
        if ordenar == "medicamentos":
            pacientes = sorted(base_list, key=lambda p: p.medicamentos.count(), reverse=True)
        elif ordenar == "inicio":
            def _inicio(p):
                m = p.medicamentos.filter(activo=True).order_by("creado_en").first()
                return m.creado_en if m else p.creado_en
            pacientes = sorted(base_list, key=_inicio, reverse=True)
        elif ordenar == "edad_asc":
            def _edad_asc(p):
                edad = p.get_edad_display()
                return (edad if edad is not None else 999, p.nombre)
            pacientes = sorted(base_list, key=_edad_asc)
        elif ordenar == "edad_desc":
            def _edad_desc(p):
                edad = p.get_edad_display()
                return (-(edad if edad is not None else 999), p.nombre)
            pacientes = sorted(base_list, key=_edad_desc)
        elif ordenar == "condicion":
            pacientes = sorted(
                base_list,
                key=lambda p: ((p.get_primera_condicion() or "zzz").lower(), p.nombre),
            )
        else:
            pacientes = list(base_qs.order_by("-es_usuario_mismo", "-creado_en"))
    else:
        pacientes = list(base_qs.order_by("-es_usuario_mismo", "-creado_en"))
    
    # Calcular estadísticas
    total_medicamentos = Medicamento.objects.filter(
        paciente__usuario=request.user,
        activo=True
    ).count()
    
    # Próximos recordatorios: medicamentos con horario fijo, expandiendo múltiples horarios (máx. 5)
    medicamentos_con_horario = Medicamento.objects.filter(
        paciente__usuario=request.user,
        activo=True,
        frecuencia_tipo=Medicamento.FRECUENCIA_HORARIO,
    ).prefetch_related('horarios').select_related('paciente')
    
    hoy = datetime.now().date()
    items = []
    for med in medicamentos_con_horario:
        horarios = med.get_horarios_ordenados()
        if not horarios:
            continue
        for h in horarios:
            items.append({'medicamento': med, 'horario': h.hora, 'fecha': hoy})
    items.sort(key=lambda x: x['horario'])
    proximos_recordatorios = items[:5]
    
    # Actividad reciente: desde Notificaciones (incluye sistema + llamadas/alertas futuras)
    notificaciones = Notificacion.objects.filter(usuario=request.user).select_related(
        "paciente", "medicamento"
    ).order_by("-creado_en")[:10]
    actividad_reciente = [
        {
            "icono": _icono_para_notificacion(n),
            "descripcion": n.titulo,
            "fecha": n.creado_en,
        }
        for n in notificaciones
    ][:5]
    
    # Días restantes del plan (calculado desde plan_expiration o 365 por defecto)
    dias_restantes_plan = perfil.get_dias_restantes_plan()
    nombre_plan = perfil.get_plan_display()

    # Llamadas esta semana (últimos 7 días) y adherencia
    desde_semana = timezone.now() - timedelta(days=7)
    llamadas_semana = Notificacion.objects.filter(
        usuario=request.user,
        tipo=Notificacion.TIPO_LLAMADA,
        creado_en__gte=desde_semana,
    ).count()
    llamadas_atendidas_semana = Notificacion.objects.filter(
        usuario=request.user,
        tipo=Notificacion.TIPO_LLAMADA,
        estado=Notificacion.ESTADO_ATENDIDA,
        creado_en__gte=desde_semana,
    ).count()
    adherencia_semana = round((llamadas_atendidas_semana / llamadas_semana * 100)) if llamadas_semana else 0

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
        "total_medicamentos": total_medicamentos,
        "proximos_recordatorios": proximos_recordatorios[:5],
        "actividad_reciente": actividad_reciente,
        "dias_restantes_plan": dias_restantes_plan,
        "nombre_plan": nombre_plan,
        "ordenar_actual": ordenar,
        "opciones_ordenar": opciones_ordenar,
        "llamadas_semana": llamadas_semana,
        "llamadas_atendidas_semana": llamadas_atendidas_semana,
        "adherencia_semana": adherencia_semana,
    }
    return render(request, "core/dashboard.html", context)


def _notifications_redirect_url(request):
    """Construye la URL de notificaciones preservando filtros (GET o POST desde formularios)."""
    from urllib.parse import urlencode
    source = request.POST if request.method == "POST" else request.GET
    params = {}
    t = source.get("tipo") or source.get("redirect_tipo")
    if t and t != "None":
        params["tipo"] = t
    p = source.get("paciente") or source.get("redirect_paciente")
    if p and p != "None":
        params["paciente"] = p
    if source.get("solo_no_leidas") == "1" or source.get("redirect_solo_no_leidas") == "1":
        params["solo_no_leidas"] = "1"
    b = source.get("buscar") or source.get("redirect_buscar")
    if b:
        params["buscar"] = b
    qs = urlencode(params) if params else ""
    base = reverse("notifications")
    return f"{base}?{qs}" if qs else base


@login_required
def notifications_view(request: HttpRequest) -> HttpResponse:
    """Vista para gestionar notificaciones con filtros y eliminación."""
    from apps.llamadas.models import Notificacion
    from apps.pacientes.models import Paciente
    from datetime import datetime, timedelta
    
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    redirect_url = _notifications_redirect_url(request)
    
    # Manejar acciones POST
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
                return redirect(redirect_url)
        
        elif action == "delete_single":
            notificacion_id = request.POST.get("notificacion_id")
            if notificacion_id:
                try:
                    notificacion = Notificacion.objects.get(id=notificacion_id, usuario=request.user)
                    notificacion.delete()
                    messages.success(request, "Notificación eliminada.")
                except Notificacion.DoesNotExist:
                    messages.error(request, "Notificación no encontrada.")
                return redirect(redirect_url)
        
        elif action == "mark_read":
            notificacion_ids = request.POST.getlist("notificacion_ids")
            if notificacion_ids:
                Notificacion.objects.filter(
                    id__in=notificacion_ids,
                    usuario=request.user
                ).update(leida=True)
                messages.success(request, f"{len(notificacion_ids)} notificación(es) marcada(s) como leída(s).")
                return redirect(redirect_url)
        
        elif action == "mark_read_single":
            notificacion_id = request.POST.get("notificacion_id")
            if notificacion_id:
                try:
                    n = Notificacion.objects.get(id=notificacion_id, usuario=request.user)
                    n.leida = True
                    n.save()
                    messages.success(request, "Marcada como leída.")
                except Notificacion.DoesNotExist:
                    pass
                return redirect(redirect_url)
        
        elif action == "mark_unread_single":
            notificacion_id = request.POST.get("notificacion_id")
            if notificacion_id:
                try:
                    n = Notificacion.objects.get(id=notificacion_id, usuario=request.user)
                    n.leida = False
                    n.save()
                    messages.success(request, "Marcada como no leída.")
                except Notificacion.DoesNotExist:
                    pass
                return redirect(redirect_url)
        
        elif action == "mark_all_read":
            Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
            messages.success(request, "Todas las notificaciones marcadas como leídas.")
            # Redirigir sin filtro "solo no leídas" para que vean la lista
            from urllib.parse import urlencode
            params = {}
            rt = request.POST.get("redirect_tipo")
            if rt and rt != "None":
                params["tipo"] = rt
            rp = request.POST.get("redirect_paciente")
            if rp and rp != "None":
                params["paciente"] = rp
            if request.POST.get("redirect_buscar"):
                params["buscar"] = request.POST.get("redirect_buscar")
            qs = urlencode(params) if params else ""
            base = reverse("notifications")
            return redirect(f"{base}?{qs}" if qs else base)
    
    # Obtener filtros (ignorar "None" como string)
    paciente_id = request.GET.get("paciente") or None
    if paciente_id == "None":
        paciente_id = None
    tipo = request.GET.get("tipo") or None
    if tipo == "None":
        tipo = None
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
    """Vista para mostrar los planes (invitados). Logueados van a Mi cuenta > Plan."""
    if request.user.is_authenticated:
        return redirect(f"{reverse('edit_profile')}?tab=planes")
    
    perfil = None
    plan_actual = None
    
    # Definir los planes con sus características (relevantes a Porvoz)
    planes_data = {
        Perfil.PLAN_FREEMIUM: {
            "nombre": "Prueba",
            "tagline": "Prueba el servicio con límites. Ideal para conocer Porvoz.",
            "precio": "$0",
            "precio_cop": None,
            "precio_mensual": 0,
            "destacado": False,
            "caracteristicas": [
                "1 Cuidador",
                "1 paciente",
                "Hasta 3 medicamentos",
                "10 llamadas automatizadas/mes",
                "Dashboard básico",
                "Historial 1 mes",
            ],
            "boton_texto": "Empezar prueba",
            "boton_estilo": "border-slate-700 text-slate-700 hover:bg-slate-50",
        },
        Perfil.PLAN_GROWTH: {
            "nombre": "Growth",
            "tagline": "Para familias. Seguimiento completo y llamadas ilimitadas.",
            "precio": "$79.900",
            "precio_cop": "79.900",
            "precio_mensual": 79900,
            "destacado": True,
            "ahorro": "Ahorra en el año",
            "caracteristicas": [
                "1 Cuidador",
                "Pacientes ilimitados",
                "Medicamentos ilimitados",
                "Llamadas ilimitadas",
                "Dashboard completo",
                "Historial 12 meses",
                "Llamadas con IA en español",
                "Alertas de adherencia",
                "Soporte por correo",
            ],
            "boton_texto": "Contratar Growth",
            "boton_estilo": "bg-slate-800 text-white hover:bg-slate-700",
        },
        Perfil.PLAN_MULTI_BUSINESS: {
            "nombre": "Multi-cuidador",
            "tagline": "Instituciones y equipos. Varios cuidadores, un solo lugar.",
            "precio": "$99.900",
            "precio_cop": "99.900",
            "precio_mensual": 99900,
            "destacado": False,
            "caracteristicas": [
                "Todo lo de Growth",
                "2 a 10 cuidadores",
                "99.900 COP por cuidador/mes",
                "Gestión centralizada",
                "Reportes consolidados",
                "Soporte prioritario",
            ],
            "boton_texto": "Contactar ventas",
            "boton_estilo": "border-slate-800 text-slate-800 hover:bg-slate-100",
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
    """Vista índice de información legal (enlaces a términos, privacidad, contacto)."""
    return render(request, "core/legal_info.html")


def terms_view(request: HttpRequest) -> HttpResponse:
    """Términos y Condiciones."""
    return render(request, "core/terms.html")


def privacy_view(request: HttpRequest) -> HttpResponse:
    """Política de Privacidad."""
    return render(request, "core/privacy.html")


def contact_view(request: HttpRequest) -> HttpResponse:
    """Contacto."""
    return render(request, "core/contact.html")


def guide_view(request: HttpRequest) -> HttpResponse:
    """Vista para mostrar la guía rápida y preguntas frecuentes."""
    return render(request, "core/guide.html")

