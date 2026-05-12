"""
Admin panel views for managing codes, users, payments, and support.
"""

from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.admin_panel.models import CodigoAcceso, ConfiguracionPlan, MensajeTicket, PagoHistorico, TicketSoporte
from apps.autenticacion.services import RegistroService
from apps.core.models import Perfil
from apps.llamadas.models import Llamada, RespuestaLlamada
from apps.usuarios.services import PerfilService


def es_admin(user):
    """Check if user is admin/staff"""
    return user.is_staff


@login_required
@user_passes_test(es_admin)
@login_required
@user_passes_test(es_admin)
def admin_dashboard(request):
    """Dashboard principal del admin"""

    # Estadísticas de usuarios
    total_usuarios = User.objects.filter(is_active=True).count()
    usuarios_activos = Perfil.objects.filter(
        plan_estado=Perfil.ESTADO_ACTIVO
    ).count()

    # Usuarios por plan
    usuarios_por_plan = (
        Perfil.objects.values("plan")
        .annotate(count=Count("user"))
        .order_by("-count")
    )

    # Ingresos este mes
    hace_30_dias = timezone.now() - timedelta(days=30)
    ingresos_mes = (
        PagoHistorico.objects.filter(
            fecha_pago__gte=hace_30_dias
        ).aggregate(total=Sum("monto"))["total"]
        or 0
    )

    # Últimos pagos
    ultimos_pagos = PagoHistorico.objects.select_related("usuario").order_by("-fecha_pago")[:10]

    # Tickets pendientes
    tickets_abiertos = TicketSoporte.objects.filter(
        estado__in=[TicketSoporte.ESTADO_ABIERTO, TicketSoporte.ESTADO_EN_PROGRESO]
    ).count()

    # Códigos disponibles
    codigos_disponibles = CodigoAcceso.objects.filter(
        estado=CodigoAcceso.ESTADO_DISPONIBLE
    ).count()

    # Estadísticas de llamadas
    total_llamadas = Llamada.objects.count()
    llamadas_completadas = Llamada.objects.filter(
        estado=Llamada.ESTADO_COMPLETADA
    ).count()
    llamadas_fallidas = Llamada.objects.filter(
        estado=Llamada.ESTADO_FALLIDA
    ).count()

    # Adherencia promedio
    respuestas_confirmadas = RespuestaLlamada.objects.filter(
        resultado=RespuestaLlamada.RESULTADO_CONFIRMADA
    ).count()
    adherencia = (
        round((respuestas_confirmadas / total_llamadas * 100) if total_llamadas > 0 else 0)
    )

    context = {
        "total_usuarios": total_usuarios,
        "usuarios_activos": usuarios_activos,
        "usuarios_por_plan": usuarios_por_plan,
        "ingresos_mes": float(ingresos_mes),
        "ultimos_pagos": ultimos_pagos,
        "tickets_abiertos": tickets_abiertos,
        "codigos_disponibles": codigos_disponibles,
        "total_llamadas": total_llamadas,
        "llamadas_completadas": llamadas_completadas,
        "llamadas_fallidas": llamadas_fallidas,
        "adherencia": adherencia,
    }

    return render(request, "admin_panel/dashboard.html", context)


@login_required
@user_passes_test(es_admin)
def crear_codigos(request):
    """Admin crea códigos de acceso y gestiona precios de planes"""

    # Manejar actualización de precios de planes
    if request.method == "POST" and request.POST.get("accion") == "actualizar_planes":
        for plan_key in [Perfil.PLAN_FREEMIUM, Perfil.PLAN_GROWTH, Perfil.PLAN_MULTI_BUSINESS, Perfil.PLAN_PROFESIONAL]:
            try:
                config = ConfiguracionPlan.objects.get(plan=plan_key)
                precio = request.POST.get(f"precio_{plan_key}")
                costo = request.POST.get(f"costo_{plan_key}")
                if precio:
                    config.precio_mensual = int(precio)
                if costo:
                    config.costo_estimado = int(costo)
                config.save()
            except ConfiguracionPlan.DoesNotExist:
                pass
        messages.success(request, "Precios de planes actualizados")
        return redirect("crear_codigos")

    # Manejar creación de códigos
    if request.method == "POST" and request.POST.get("accion") == "crear_codigos":
        plan = request.POST.get("plan")
        cantidad = int(request.POST.get("cantidad", 1))
        duracion_meses = int(request.POST.get("duracion_meses", 1))
        notas = request.POST.get("notas", "")

        dias_limite = int(request.POST.get("dias_limite_canje", 60))
        fecha_limite = date.today() + timedelta(days=dias_limite)

        codigos_creados = []
        for _ in range(cantidad):
            codigo = CodigoAcceso.objects.create(
                codigo=CodigoAcceso.generar_codigo(),
                plan=plan,
                duracion_meses=duracion_meses,
                notas=notas,
                creado_por=request.user,
                fecha_limite_canje=fecha_limite,
            )
            codigos_creados.append(codigo)

        messages.success(request, f"{cantidad} código(s) creado(s)")

        plan_display = dict(Perfil.PLAN_CHOICES).get(plan, plan)
        context = {
            "codigos": codigos_creados,
            "plan_display": plan_display,
            "duracion_meses": duracion_meses,
        }
        return render(request, "admin_panel/codigos_creados.html", context)

    # GET: mostrar formulario
    configuraciones = ConfiguracionPlan.objects.all()
    planes_info = []
    for config in configuraciones:
        planes_info.append({
            "plan_key": config.plan,
            "nombre": config.nombre,
            "precio": f"${config.precio_mensual:,.0f}" if config.precio_mensual else "$0",
            "precio_mensual": config.precio_mensual,
            "costo_estimado": config.costo_estimado,
            "margen": config.margen_neto(),
            "porcentaje_margen": config.porcentaje_margen(),
            "limite_pacientes": config.limite_pacientes,
            "limite_medicamentos": config.limite_medicamentos or "Ilimitado",
            "limite_llamadas": config.limite_llamadas_mes,
        })

    context = {
        "planes": Perfil.PLAN_CHOICES,
        "planes_info": planes_info,
        "configuraciones": configuraciones,
    }
    return render(request, "admin_panel/crear_codigos.html", context)


@login_required
@user_passes_test(es_admin)
def ver_codigos(request):
    """Ver todos los códigos creados"""

    filtro_estado = request.GET.get("estado", "")

    codigos = CodigoAcceso.objects.select_related("usuario_usado_por").all()

    if filtro_estado:
        codigos = codigos.filter(estado=filtro_estado)

    # Estadísticas por estado
    total_codigos = CodigoAcceso.objects.count()
    codigos_disponibles = CodigoAcceso.objects.filter(estado=CodigoAcceso.ESTADO_DISPONIBLE).count()
    codigos_usados = CodigoAcceso.objects.filter(estado=CodigoAcceso.ESTADO_USADO).count()
    codigos_expirados = CodigoAcceso.objects.filter(estado=CodigoAcceso.ESTADO_EXPIRADO).count()

    context = {
        "codigos": codigos,
        "total_codigos": total_codigos,
        "codigos_disponibles": codigos_disponibles,
        "codigos_usados": codigos_usados,
        "codigos_expirados": codigos_expirados,
        "estado_filtro": filtro_estado,
        "estados": CodigoAcceso.ESTADO_CHOICES,
    }
    return render(request, "admin_panel/ver_codigos.html", context)


@login_required
@user_passes_test(es_admin)
def ver_usuarios(request):
    """Ver y gestionar usuarios con filtros por pill"""
    from datetime import date as _date

    busqueda = request.GET.get("q", "")
    filtro = request.GET.get("filtro", "todos")

    base_qs = User.objects.filter(is_staff=False).prefetch_related("perfil", "pacientes")

    hoy = _date.today()
    limite_vencimiento = hoy + timedelta(days=7)

    total = base_qs.count()
    activos = base_qs.filter(is_active=True).count()
    inactivos = base_qs.filter(is_active=False).count()
    por_vencer = base_qs.filter(
        is_active=True,
        perfil__plan_expiration__lte=limite_vencimiento,
        perfil__plan_expiration__gte=hoy,
    ).count()

    usuarios = base_qs
    if filtro == "activos":
        usuarios = usuarios.filter(is_active=True)
    elif filtro == "inactivos":
        usuarios = usuarios.filter(is_active=False)
    elif filtro == "por_vencer":
        usuarios = usuarios.filter(
            is_active=True,
            perfil__plan_expiration__lte=limite_vencimiento,
            perfil__plan_expiration__gte=hoy,
        )

    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda)
            | Q(email__icontains=busqueda)
            | Q(first_name__icontains=busqueda)
        )

    usuarios = usuarios.order_by("-date_joined")

    context = {
        "usuarios": usuarios,
        "total_usuarios": total,
        "usuarios_activos": activos,
        "busqueda": busqueda,
        "filtro_activo": filtro,
        "filtros_disponibles": [
            ("todos",      "Todos",           total),
            ("activos",    "Activos",         activos),
            ("inactivos",  "Inactivos",       inactivos),
            ("por_vencer", "Plan por vencer", por_vencer),
        ],
    }
    return render(request, "admin_panel/ver_usuarios.html", context)


@login_required
@user_passes_test(es_admin)
def historial_pagos(request):
    """Ver historial completo de pagos"""

    filtro_plan = request.GET.get("plan", "")
    filtro_tipo = request.GET.get("tipo_pago", "")

    pagos = PagoHistorico.objects.select_related("usuario", "codigo_usado").all().order_by("-fecha_pago")

    if filtro_plan:
        pagos = pagos.filter(plan=filtro_plan)
    if filtro_tipo:
        pagos = pagos.filter(tipo_pago=filtro_tipo)

    todos_pagos = PagoHistorico.objects.all()
    hace_30 = timezone.now() - timedelta(days=30)
    hace_60 = timezone.now() - timedelta(days=60)

    ingresos_mes = todos_pagos.filter(fecha_pago__gte=hace_30).aggregate(t=Sum("monto"))["t"] or 0
    ingresos_mes_ant = todos_pagos.filter(fecha_pago__gte=hace_60, fecha_pago__lt=hace_30).aggregate(t=Sum("monto"))["t"] or 0
    total_ingresos = todos_pagos.aggregate(t=Sum("monto"))["t"] or 0
    promedio_pago = (total_ingresos / todos_pagos.count()) if todos_pagos.count() > 0 else 0

    por_plan = (
        todos_pagos.values("plan")
        .annotate(total=Sum("monto"), cantidad=Count("id"))
        .order_by("-total")
    )
    por_tipo = (
        todos_pagos.values("tipo_pago")
        .annotate(cantidad=Count("id"))
        .order_by("-cantidad")
    )

    variacion = 0
    if ingresos_mes_ant > 0:
        variacion = round((float(ingresos_mes) - float(ingresos_mes_ant)) / float(ingresos_mes_ant) * 100)

    context = {
        "pagos": pagos,
        "total_ingresos": float(total_ingresos),
        "promedio_pago": float(promedio_pago),
        "ingresos_mes": float(ingresos_mes),
        "variacion_mes": variacion,
        "por_plan": por_plan,
        "por_tipo": por_tipo,
        "planes": Perfil.PLAN_CHOICES,
        "tipos": PagoHistorico.TIPO_CHOICES,
        "filtro_plan": filtro_plan,
        "filtro_tipo": filtro_tipo,
    }
    return render(request, "admin_panel/historial_pagos.html", context)


@login_required
@user_passes_test(es_admin)
def tickets_soporte(request):
    """Ver y gestionar tickets de soporte"""

    filtro_estado = request.GET.get("estado", "")

    tickets = TicketSoporte.objects.select_related("usuario", "asignado_a").all().order_by("-creado_en")

    if filtro_estado:
        tickets = tickets.filter(estado=filtro_estado)

    # Estadísticas
    total_tickets = TicketSoporte.objects.count()
    tickets_abiertos = TicketSoporte.objects.filter(estado=TicketSoporte.ESTADO_ABIERTO).count()
    tickets_progreso = TicketSoporte.objects.filter(estado=TicketSoporte.ESTADO_EN_PROGRESO).count()
    tickets_resueltos = TicketSoporte.objects.filter(estado=TicketSoporte.ESTADO_RESUELTO).count()

    context = {
        "tickets": tickets,
        "total_tickets": total_tickets,
        "tickets_abiertos": tickets_abiertos,
        "tickets_progreso": tickets_progreso,
        "tickets_resueltos": tickets_resueltos,
        "estados": TicketSoporte.ESTADO_CHOICES,
        "filtro_estado": filtro_estado,
    }
    return render(request, "admin_panel/tickets_soporte.html", context)


# ─── TICKET DETAIL / CHAT ────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def ticket_detalle(request, ticket_id):
    """Vista de chat para un ticket específico"""
    try:
        ticket = TicketSoporte.objects.select_related("usuario", "asignado_a").get(id=ticket_id)
    except TicketSoporte.DoesNotExist:
        messages.error(request, "Ticket no encontrado.")
        return redirect("tickets_soporte")

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "responder":
            contenido = request.POST.get("contenido", "").strip()
            if contenido:
                MensajeTicket.objects.create(
                    ticket=ticket,
                    autor=request.user,
                    es_admin=True,
                    contenido=contenido,
                )
                if ticket.estado == TicketSoporte.ESTADO_ABIERTO:
                    ticket.estado = TicketSoporte.ESTADO_EN_PROGRESO
                    ticket.save()

                # Enviar notificación al usuario si tiene cuenta
                if ticket.usuario:
                    from apps.notificaciones.models import Notificacion
                    Notificacion.objects.create(
                        usuario=ticket.usuario,
                        titulo=f"Respuesta en tu ticket: {ticket.titulo[:50]}",
                        mensaje=contenido[:100] + ("..." if len(contenido) > 100 else ""),
                        tipo=Notificacion.TIPO_SOPORTE,
                        url=f"/soporte/tickets/{ticket.id}/",
                        es_leida=False,
                    )
                messages.success(request, "Respuesta enviada y notificación enviada al usuario.")

        elif accion == "cambiar_estado":
            nuevo_estado = request.POST.get("estado")
            if nuevo_estado in dict(TicketSoporte.ESTADO_CHOICES):
                ticket.estado = nuevo_estado
                if nuevo_estado == TicketSoporte.ESTADO_RESUELTO:
                    ticket.resuelto_en = timezone.now()
                ticket.save()

        elif accion == "cambiar_prioridad":
            nueva_prioridad = request.POST.get("prioridad")
            if nueva_prioridad in dict(TicketSoporte.PRIORIDAD_CHOICES):
                ticket.prioridad = nueva_prioridad
                ticket.save()

        return redirect("ticket_detalle", ticket_id=ticket.id)

    mensajes = ticket.mensajes.select_related("autor").all()
    context = {
        "ticket": ticket,
        "mensajes": mensajes,
        "estados": TicketSoporte.ESTADO_CHOICES,
        "prioridades": TicketSoporte.PRIORIDAD_CHOICES,
    }
    return render(request, "admin_panel/ticket_detalle.html", context)


# ─── CONTACTO PÚBLICO ─────────────────────────────────────────────────────────

def contactar_soporte(request):
    """Formulario de contacto público — crea ticket sin necesitar cuenta"""
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        asunto = request.POST.get("asunto", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()

        if not (nombre and email and asunto and descripcion):
            messages.error(request, "Por favor completa todos los campos obligatorios.")
        else:
            ticket = TicketSoporte.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                nombre_contacto=nombre,
                email_contacto=email,
                telefono_contacto=telefono,
                titulo=asunto,
                descripcion=descripcion,
            )
            # Primer mensaje = la descripción
            MensajeTicket.objects.create(
                ticket=ticket,
                autor=request.user if request.user.is_authenticated else None,
                es_admin=False,
                contenido=descripcion,
            )
            messages.success(
                request,
                "¡Mensaje enviado! Nuestro equipo te contactará pronto al correo indicado."
            )
            return redirect("contactar_soporte")

    return render(request, "admin_panel/contactar_soporte.html")


# ─── ADMIN: EDITAR USUARIO ────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def editar_usuario(request, usuario_id):
    """Admin edita datos, plan, estado y contraseña de un usuario"""
    try:
        usuario = User.objects.select_related("perfil").get(id=usuario_id, is_staff=False)
    except User.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")
        return redirect("admin_usuarios")

    perfil = usuario.perfil

    if request.method == "POST":
        accion = request.POST.get("accion", "datos")

        if accion == "datos":
            usuario.first_name = request.POST.get("first_name", "").strip()
            usuario.last_name = request.POST.get("last_name", "").strip()
            nuevo_username = request.POST.get("username", "").strip()
            nuevo_email = request.POST.get("email", "").strip()

            if nuevo_username and nuevo_username != usuario.username:
                if User.objects.filter(username=nuevo_username).exclude(id=usuario.id).exists():
                    messages.error(request, "Ese nombre de usuario ya está en uso.")
                    return redirect(f"{request.path}?seccion=datos")
                usuario.username = nuevo_username

            if nuevo_email:
                usuario.email = nuevo_email

            usuario.is_active = request.POST.get("is_active") == "on"
            usuario.save()

            # Guardar campos del perfil extendido
            perfil.city = request.POST.get("city", "").strip()
            perfil.phone = request.POST.get("phone", "").strip()
            perfil.document_type = request.POST.get("document_type", "").strip()
            perfil.document_number = request.POST.get("document_number", "").strip()
            perfil.emergency_contact_name = request.POST.get("emergency_contact_name", "").strip()
            perfil.emergency_contact_phone = request.POST.get("emergency_contact_phone", "").strip()
            dob_str = request.POST.get("date_of_birth", "").strip()
            if dob_str:
                try:
                    from datetime import datetime as _dt
                    perfil.date_of_birth = _dt.strptime(dob_str, "%Y-%m-%d").date()
                except ValueError:
                    pass
            perfil.save()
            messages.success(request, "Datos actualizados correctamente.")

        elif accion == "cambiar_plan":
            nuevo_plan = request.POST.get("plan")
            duracion = int(request.POST.get("duracion_meses", 1))
            if nuevo_plan in dict(Perfil.PLAN_CHOICES):
                perfil.plan = nuevo_plan
                perfil.plan_estado = Perfil.ESTADO_ACTIVO
                perfil.plan_pausa_hasta = None
                perfil.plan_cancelacion_fecha = None
                if nuevo_plan == Perfil.PLAN_FREEMIUM:
                    perfil.plan_expiration = None
                else:
                    base = perfil.plan_expiration if perfil.plan_expiration and perfil.plan_expiration > date.today() else date.today()
                    perfil.plan_expiration = base + timedelta(days=duracion * 30)
                perfil.save()
                messages.success(request, f"Plan cambiado a {perfil.get_plan_display()}.")
            else:
                messages.error(request, "Plan inválido.")

        elif accion == "extender_plan":
            dias_extra = int(request.POST.get("dias_extra", 0))
            if dias_extra > 0:
                base = perfil.plan_expiration if perfil.plan_expiration and perfil.plan_expiration > date.today() else date.today()
                perfil.plan_expiration = base + timedelta(days=dias_extra)
                perfil.save()
                messages.success(request, f"{dias_extra} días añadidos. Nuevo vencimiento: {perfil.plan_expiration.strftime('%d/%m/%Y')}.")

        elif accion == "suspender":
            perfil.plan_estado = Perfil.ESTADO_PAUSADO
            perfil.save()
            messages.success(request, "Plan suspendido.")

        elif accion == "reactivar":
            perfil.plan_estado = Perfil.ESTADO_ACTIVO
            perfil.save()
            messages.success(request, "Plan reactivado.")

        elif accion == "password":
            nueva_password = request.POST.get("nueva_password", "")
            confirmar = request.POST.get("confirmar_password", "")
            if len(nueva_password) < 8:
                messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            elif nueva_password != confirmar:
                messages.error(request, "Las contraseñas no coinciden.")
            else:
                usuario.set_password(nueva_password)
                usuario.save()
                messages.success(request, "Contraseña cambiada correctamente.")

        seccion_destino = {"datos": "datos", "password": "password"}.get(accion, "plan")
        return redirect(f"{request.path}?seccion={seccion_destino}")

    seccion = request.GET.get("seccion", "datos")
    if seccion not in ("datos", "plan", "password", "tickets"):
        seccion = "datos"

    from datetime import date as _date
    dias_restantes = None
    if perfil.plan_expiration:
        dias_restantes = (perfil.plan_expiration - _date.today()).days

    context = {
        "usuario": usuario,
        "perfil": perfil,
        "planes": Perfil.PLAN_CHOICES,
        "tickets": TicketSoporte.objects.filter(usuario=usuario).order_by("-creado_en")[:10],
        "seccion": seccion,
        "dias_restantes": dias_restantes,
        "tab_list": [
            ("datos",    "person-lines-fill", "Datos"),
            ("plan",     "star",              "Plan"),
            ("password", "shield-lock",       "Contraseña"),
            ("tickets",  "chat-dots",         "Tickets"),
        ],
    }
    return render(request, "admin_panel/editar_usuario.html", context)


# ─── ADMIN: CREAR PAGO MANUAL ─────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def crear_pago_manual(request):
    """Admin registra manualmente un pago/cambio de plan con comprobante opcional"""
    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        plan = request.POST.get("plan")
        tipo_pago = request.POST.get("tipo_pago")
        metodo_transferencia = request.POST.get("metodo_transferencia", "")
        monto = request.POST.get("monto") or None
        referencia = request.POST.get("referencia_pago", "").strip()
        notas = request.POST.get("notas", "").strip()
        duracion_meses = int(request.POST.get("duracion_meses", 1))
        comprobante = request.FILES.get("comprobante")

        try:
            usuario = User.objects.get(id=usuario_id, is_staff=False)
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect("crear_pago_manual")

        if not (plan and tipo_pago):
            messages.error(request, "Plan y tipo de pago son obligatorios.")
            return redirect("crear_pago_manual")

        # Actualizar el plan del usuario
        perfil = usuario.perfil
        perfil.plan = plan
        perfil.plan_estado = Perfil.ESTADO_ACTIVO
        perfil.plan_expiration = date.today() + timedelta(days=30 * duracion_meses)
        perfil.save()

        # Registrar pago
        pago = PagoHistorico.objects.create(
            usuario=usuario,
            plan=plan,
            duracion_meses=duracion_meses,
            tipo_pago=tipo_pago,
            metodo_transferencia=metodo_transferencia,
            monto=monto,
            referencia_pago=referencia,
            notas=notas,
            procesado_por=request.user,
            fecha_hasta=perfil.plan_expiration,
        )
        if comprobante:
            pago.comprobante = comprobante
            pago.save()

        messages.success(
            request,
            f"Pago registrado y plan '{perfil.get_plan_display()}' activado para {usuario.get_full_name() or usuario.username}."
        )
        return redirect("historial_pagos")

    usuarios = User.objects.filter(is_staff=False, is_active=True).order_by("first_name", "username")

    # Precios por plan desde DB (fallback a hardcodeados)
    precios_planes = {}
    for plan_key, plan_display in Perfil.PLAN_CHOICES:
        try:
            config = ConfiguracionPlan.objects.get(plan=plan_key)
            precios_planes[plan_key] = int(config.precio_mensual)
        except ConfiguracionPlan.DoesNotExist:
            # Fallback a valores por defecto
            defaults = {
                Perfil.PLAN_FREEMIUM: 0,
                Perfil.PLAN_GROWTH: 24_900,
                Perfil.PLAN_MULTI_BUSINESS: 59_900,
                Perfil.PLAN_PROFESIONAL: 139_900,
            }
            precios_planes[plan_key] = defaults.get(plan_key, 0)

    context = {
        "usuarios": usuarios,
        "planes": Perfil.PLAN_CHOICES,
        "tipos_pago": PagoHistorico.TIPO_CHOICES,
        "metodos": PagoHistorico.METODO_CHOICES,
        "precios_planes": precios_planes,
    }
    return render(request, "admin_panel/crear_pago_manual.html", context)


# ─── ADMIN: CREAR USUARIO ────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin)
def crear_usuario_admin(request):
    """Admin crea un nuevo usuario con los mismos datos que el registro normal."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        date_of_birth_str = request.POST.get("date_of_birth", "").strip()
        city = request.POST.get("city", "").strip()
        phone_country = request.POST.get("phone_country", "+57").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        document_type = request.POST.get("document_type", "").strip()
        document_number = request.POST.get("document_number", "").strip()
        emergency_contact_name = request.POST.get("emergency_contact_name", "").strip()
        emergency_contact_phone_country = request.POST.get("emergency_contact_phone_country", "+57").strip()
        emergency_contact_phone_number = request.POST.get("emergency_contact_phone_number", "").strip()
        plan = request.POST.get("plan", Perfil.PLAN_FREEMIUM)

        if not all([username, email, password, first_name, last_name]):
            messages.error(request, "Por favor completa todos los campos obligatorios.")
        elif password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif len(password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, f"El usuario '{username}' ya está registrado.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, f"El correo '{email}' ya tiene una cuenta.")
        else:
            birth_date_obj = None
            if date_of_birth_str:
                birth_date_obj, error_msg = PerfilService.validar_edad(date_of_birth_str)
                if error_msg:
                    messages.error(request, error_msg)
                    return render(request, "admin_panel/crear_usuario.html", {"planes": Perfil.PLAN_CHOICES})

            try:
                usuario, perfil = RegistroService.crear_usuario_y_perfil(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_country=phone_country,
                    phone_number=phone_number,
                    document_type=document_type,
                    document_number=document_number,
                    date_of_birth=birth_date_obj,
                    city=city,
                    emergency_contact_name=emergency_contact_name,
                    emergency_contact_phone_country=emergency_contact_phone_country,
                    emergency_contact_phone_number=emergency_contact_phone_number,
                )
                # Asignar el plan elegido por el admin
                if plan and plan != Perfil.PLAN_FREEMIUM:
                    perfil.plan = plan
                    perfil.plan_expiration = date.today() + timedelta(days=30)
                    perfil.save()

                messages.success(request, f"Usuario '{username}' creado con plan {perfil.get_plan_display()}.")
                return redirect("editar_usuario", usuario_id=usuario.id)
            except Exception:
                messages.error(request, "Error al crear el usuario. Verifica los datos e intenta de nuevo.")

    context = {"planes": Perfil.PLAN_CHOICES}
    return render(request, "admin_panel/crear_usuario.html", context)


# ─── USUARIO: VER MIS TICKETS ─────────────────────────────────────────────────

@login_required
def mis_tickets(request):
    """Lista de tickets del usuario autenticado"""
    if request.user.is_staff:
        return redirect("tickets_soporte")

    tickets = TicketSoporte.objects.filter(usuario=request.user).order_by("-creado_en")
    context = {
        "tickets": tickets,
        "titulo": "Mis Solicitudes de Soporte",
    }
    return render(request, "soporte/mis_tickets.html", context)


@login_required
def mi_ticket_detalle(request, ticket_id):
    """Detalle de un ticket para el usuario (ver conversación y responder)"""
    if request.user.is_staff:
        return redirect("ticket_detalle", ticket_id=ticket_id)

    try:
        ticket = TicketSoporte.objects.select_related("asignado_a").get(id=ticket_id, usuario=request.user)
    except TicketSoporte.DoesNotExist:
        messages.error(request, "Ticket no encontrado.")
        return redirect("mis_tickets")

    if request.method == "POST":
        contenido = request.POST.get("contenido", "").strip()
        if contenido:
            MensajeTicket.objects.create(
                ticket=ticket,
                autor=request.user,
                es_admin=False,
                contenido=contenido,
            )
            if ticket.estado == TicketSoporte.ESTADO_RESUELTO:
                ticket.estado = TicketSoporte.ESTADO_ABIERTO
            ticket.save()
            messages.success(request, "Tu mensaje ha sido enviado.")
            return redirect("mi_ticket_detalle", ticket_id=ticket.id)

    mensajes = ticket.mensajes.select_related("autor").all()
    context = {
        "ticket": ticket,
        "mensajes": mensajes,
        "es_usuario": True,
    }
    return render(request, "soporte/mi_ticket_detalle.html", context)
