"""
Datos de planes, límites y verificación de cuotas.

Costo real por llamada (Twilio Colombia ~$0.013 USD/min, 1.5 min promedio, $4.100 COP/USD):
    ~$80 COP por llamada

Planes:
    Gratuito  ($0):           15 llamadas  → costo ~$1.200 COP  (adquisición)
    Básico    ($24.900):      90 llamadas  → costo ~$7.200 COP  → margen ~$13.000 COP (52%)
    Familiar  ($59.900):     300 llamadas  → costo ~$24.000 COP → margen ~$27.000 COP (45%)
    Profesional ($139.900):  900 llamadas  → costo ~$72.000 COP → margen ~$58.000 COP (42%)
"""

from datetime import date, timedelta

from apps.core.models import Perfil

# ------------------------------------------------------------------
# Límites por plan
# ------------------------------------------------------------------

PLAN_LIMITS = {
    Perfil.PLAN_FREEMIUM: {
        "max_pacientes": 1,
        "max_medicamentos_por_paciente": 2,
        "max_llamadas_mes": 15,
    },
    Perfil.PLAN_GROWTH: {
        "max_pacientes": 1,
        "max_medicamentos_por_paciente": 5,
        "max_llamadas_mes": 90,
    },
    Perfil.PLAN_MULTI_BUSINESS: {
        "max_pacientes": 4,
        "max_medicamentos_por_paciente": None,  # ilimitado
        "max_llamadas_mes": 300,
    },
    Perfil.PLAN_PROFESIONAL: {
        "max_pacientes": 10,
        "max_medicamentos_por_paciente": None,  # ilimitado
        "max_llamadas_mes": 900,
    },
}

# ------------------------------------------------------------------
# Datos de planes para la UI
# ------------------------------------------------------------------

PLANES_DATA = {
    Perfil.PLAN_FREEMIUM: {
        "nombre": "Gratuito",
        "tagline": "Prueba Porvoz sin costo. Sin tarjeta requerida.",
        "precio": "$0",
        "precio_cop": None,
        "precio_mensual": 0,
        "destacado": False,
        "caracteristicas": [
            "1 paciente",
            "Hasta 2 medicamentos",
            "15 llamadas automatizadas/mes",
            "Dashboard básico",
        ],
        "no_incluye": [
            "Soporte prioritario",
            "Historial extendido",
        ],
        "limites": PLAN_LIMITS[Perfil.PLAN_FREEMIUM],
        "boton_texto": "Empezar gratis",
        "boton_estilo": "border border-slate-300 text-slate-700 hover:bg-slate-50",
        "color_badge": "bg-slate-100 text-slate-600",
    },
    Perfil.PLAN_GROWTH: {
        "nombre": "Básico",
        "tagline": "Un paciente bajo control total, todos los días.",
        "precio": "$24.900",
        "precio_cop": "24.900",
        "precio_mensual": 24900,
        "destacado": False,
        "caracteristicas": [
            "1 paciente",
            "Hasta 5 medicamentos",
            "90 llamadas automatizadas/mes",
            "Dashboard completo",
            "Historial 3 meses",
            "Alertas por correo",
        ],
        "limites": PLAN_LIMITS[Perfil.PLAN_GROWTH],
        "boton_texto": "Contratar Básico",
        "boton_estilo": "border border-slate-700 text-slate-700 hover:bg-slate-50",
        "color_badge": "bg-blue-100 text-blue-700",
    },
    Perfil.PLAN_MULTI_BUSINESS: {
        "nombre": "Familiar",
        "tagline": "Cuida a toda la familia desde un solo lugar.",
        "precio": "$59.900",
        "precio_cop": "59.900",
        "precio_mensual": 59900,
        "destacado": True,
        "caracteristicas": [
            "Hasta 4 pacientes",
            "Medicamentos ilimitados",
            "300 llamadas automatizadas/mes",
            "Dashboard completo",
            "Historial 6 meses",
            "Alertas de adherencia",
            "Soporte por correo",
        ],
        "limites": PLAN_LIMITS[Perfil.PLAN_MULTI_BUSINESS],
        "boton_texto": "Contratar Familiar",
        "boton_estilo": "bg-slate-800 text-white hover:bg-slate-700",
        "color_badge": "bg-indigo-100 text-indigo-700",
    },
    Perfil.PLAN_PROFESIONAL: {
        "nombre": "Profesional",
        "tagline": "Para cuidadores independientes y equipos de salud.",
        "precio": "$139.900",
        "precio_cop": "139.900",
        "precio_mensual": 139900,
        "destacado": False,
        "caracteristicas": [
            "Hasta 10 pacientes",
            "Medicamentos ilimitados",
            "900 llamadas automatizadas/mes",
            "Dashboard completo",
            "Historial completo",
            "Reportes de adherencia en PDF",
            "Alertas de adherencia",
            "Soporte prioritario",
        ],
        "limites": PLAN_LIMITS[Perfil.PLAN_PROFESIONAL],
        "boton_texto": "Contratar Profesional",
        "boton_estilo": "border border-slate-800 text-slate-800 hover:bg-slate-100",
        "color_badge": "bg-amber-100 text-amber-700",
    },
}

_ORDEN_PLANES = [
    Perfil.PLAN_FREEMIUM,
    Perfil.PLAN_GROWTH,
    Perfil.PLAN_MULTI_BUSINESS,
    Perfil.PLAN_PROFESIONAL,
]


def _caracteristicas_desde_config(config, plan_key: str) -> list[str]:
    """Genera la lista de características dinámicamente desde ConfiguracionPlan."""
    pac = config.limite_pacientes
    med = config.limite_medicamentos
    llamadas = config.limite_llamadas_mes

    caracteristicas = [
        f"{pac} paciente" if pac == 1 else f"Hasta {pac} pacientes",
        "Medicamentos ilimitados" if med is None else f"Hasta {med} medicamento{'s' if med != 1 else ''} por paciente",
        f"{llamadas} llamada{'s' if llamadas != 1 else ''} automatizada{'s' if llamadas != 1 else ''}/mes",
    ]

    # Características fijas por nivel de plan (dashboard, historial, soporte)
    extras_por_plan = {
        Perfil.PLAN_FREEMIUM: ["Dashboard básico"],
        Perfil.PLAN_GROWTH: ["Dashboard completo", "Historial 3 meses", "Alertas por correo"],
        Perfil.PLAN_MULTI_BUSINESS: ["Dashboard completo", "Historial 6 meses", "Alertas de adherencia", "Soporte por correo"],
        Perfil.PLAN_PROFESIONAL: [
            "Dashboard completo", "Historial completo",
            "Reportes de adherencia en PDF", "Alertas de adherencia", "Soporte prioritario",
        ],
    }
    caracteristicas.extend(extras_por_plan.get(plan_key, []))
    return caracteristicas


def obtener_planes(plan_actual: str | None = None) -> list[dict]:
    """Retorna la lista de planes desde DB con límites actualizados de ConfiguracionPlan."""
    try:
        from apps.admin_panel.models import ConfiguracionPlan
        configuraciones = ConfiguracionPlan.objects.filter(activo=True).order_by("precio_mensual")
        planes = []
        for config in configuraciones:
            limites = {
                "max_pacientes": config.limite_pacientes,
                "max_medicamentos_por_paciente": config.limite_medicamentos,
                "max_llamadas_mes": config.limite_llamadas_mes,
            }

            plan_dict = {
                "plan_key": config.plan,
                "nombre": config.nombre,
                "tagline": config.descripcion or PLANES_DATA.get(config.plan, {}).get("tagline", ""),
                "precio": f"${config.precio_mensual:,.0f}" if config.precio_mensual else "$0",
                "precio_cop": str(int(config.precio_mensual)) if config.precio_mensual else None,
                "precio_mensual": int(config.precio_mensual),
                "destacado": PLANES_DATA.get(config.plan, {}).get("destacado", False),
                "caracteristicas": _caracteristicas_desde_config(config, config.plan),
                "no_incluye": PLANES_DATA.get(config.plan, {}).get("no_incluye", []),
                "limites": limites,
                "boton_texto": PLANES_DATA.get(config.plan, {}).get("boton_texto", "Contratar"),
                "boton_estilo": PLANES_DATA.get(config.plan, {}).get("boton_estilo", ""),
                "color_badge": PLANES_DATA.get(config.plan, {}).get("color_badge", ""),
                "costo_estimado": int(config.costo_estimado),
                "margen_neto": config.margen_neto(),
                "porcentaje_margen": config.porcentaje_margen(),
            }
            planes.append(plan_dict)

        for plan in planes:
            plan["es_plan_actual"] = (
                plan_actual == plan["plan_key"] if plan_actual else False
            )
        return planes
    except Exception:
        # Fallback a datos hardcodeados si hay error con DB
        planes = [
            {**PLANES_DATA[key], "plan_key": key}
            for key in _ORDEN_PLANES
        ]
        for plan in planes:
            plan["es_plan_actual"] = (
                plan_actual == plan["plan_key"] if plan_actual else False
            )
        return planes


# ------------------------------------------------------------------
# Historial de facturación (simulado para UI)
# ------------------------------------------------------------------

def generar_historial_facturacion(perfil) -> list[dict]:
    """Genera historial de facturación simulado para la UI."""
    if perfil.plan == Perfil.PLAN_FREEMIUM:
        return []
    datos = PLANES_DATA.get(perfil.plan, {})
    precio = datos.get("precio_mensual", 0)
    nombre = datos.get("nombre", "")
    if not precio:
        return []
    base = perfil.plan_expiration or date.today()
    historial = []
    for i in range(3):
        fecha_cobro = base - timedelta(days=30 * i)
        if fecha_cobro > date.today():
            continue
        monto = f"${precio:,.0f}".replace(",", ".")
        historial.append({
            "fecha": fecha_cobro,
            "descripcion": f"Plan {nombre} — suscripción mensual",
            "monto": f"{monto} COP",
            "estado": "Pagado",
        })
    return historial


# ------------------------------------------------------------------
# PlanService — verificación de cuotas
# ------------------------------------------------------------------

class PlanService:
    """Verifica límites del plan activo de un usuario."""

    @staticmethod
    def get_limites(plan: str) -> dict:
        try:
            from apps.admin_panel.models import ConfiguracionPlan
            config = ConfiguracionPlan.objects.get(plan=plan)
            return {
                "max_pacientes": config.limite_pacientes,
                "max_medicamentos_por_paciente": config.limite_medicamentos,
                "max_llamadas_mes": config.limite_llamadas_mes,
            }
        except Exception:
            return PLAN_LIMITS.get(plan, PLAN_LIMITS[Perfil.PLAN_FREEMIUM])

    @staticmethod
    def puede_agregar_paciente(usuario) -> tuple[bool, str | None]:
        from apps.pacientes.models import Paciente

        perfil = usuario.perfil
        limites = PlanService.get_limites(perfil.plan)
        max_p = limites["max_pacientes"]
        actual = Paciente.objects.filter(usuario=usuario, activo=True).count()
        if actual >= max_p:
            nombre_plan = PLANES_DATA.get(perfil.plan, {}).get("nombre", perfil.plan)
            return (
                False,
                f"Tu plan {nombre_plan} permite máximo {max_p} paciente(s). "
                "Actualiza tu plan para agregar más.",
            )
        return True, None

    @staticmethod
    def puede_agregar_medicamento(usuario, paciente) -> tuple[bool, str | None]:
        from apps.medicamentos.models import Medicamento

        perfil = usuario.perfil
        limites = PlanService.get_limites(perfil.plan)
        max_m = limites["max_medicamentos_por_paciente"]
        if max_m is None:
            return True, None
        actual = Medicamento.objects.filter(paciente=paciente, activo=True).count()
        if actual >= max_m:
            nombre_plan = PLANES_DATA.get(perfil.plan, {}).get("nombre", perfil.plan)
            return (
                False,
                f"Tu plan {nombre_plan} permite máximo {max_m} medicamento(s) por paciente. "
                "Actualiza tu plan para agregar más.",
            )
        return True, None

    @staticmethod
    def puede_realizar_llamada(usuario) -> tuple[bool, str | None]:
        from apps.llamadas.models import Llamada

        perfil = usuario.perfil
        hoy = date.today()

        if perfil.plan_estado == Perfil.ESTADO_PAUSADO:
            return False, "Tu plan está pausado. Reactívalo para continuar con las llamadas."
        if perfil.plan_estado == Perfil.ESTADO_CANCELADO and perfil.plan_cancelacion_fecha and perfil.plan_cancelacion_fecha <= hoy:
            return False, "Tu plan fue cancelado. Activa un nuevo plan para continuar."

        if perfil.plan != Perfil.PLAN_FREEMIUM and perfil.plan_expiration and perfil.plan_expiration < hoy:
            return (
                False,
                f"Tu plan {perfil.get_plan_display()} venció el {perfil.plan_expiration.strftime('%d/%m/%Y')}. "
                "Renuévalo para continuar realizando llamadas.",
            )

        limites = PlanService.get_limites(perfil.plan)
        max_l = limites["max_llamadas_mes"]
        llamadas_mes = Llamada.objects.filter(
            usuario=usuario,
            fecha_programada__year=hoy.year,
            fecha_programada__month=hoy.month,
        ).count()
        if llamadas_mes >= max_l:
            nombre_plan = PLANES_DATA.get(perfil.plan, {}).get("nombre", perfil.plan)
            return (
                False,
                f"Alcanzaste el límite de {max_l} llamada(s)/mes de tu plan {nombre_plan}. "
                "Actualiza tu plan para continuar.",
            )
        return True, None

    @staticmethod
    def get_uso_actual(usuario) -> dict:
        from apps.llamadas.models import Llamada
        from apps.pacientes.models import Paciente

        perfil = usuario.perfil
        limites = PlanService.get_limites(perfil.plan)
        hoy = date.today()

        pacientes = Paciente.objects.filter(usuario=usuario, activo=True).count()
        llamadas_mes = Llamada.objects.filter(
            usuario=usuario,
            fecha_programada__year=hoy.year,
            fecha_programada__month=hoy.month,
        ).count()

        return {
            "pacientes": pacientes,
            "max_pacientes": limites["max_pacientes"],
            "llamadas_mes": llamadas_mes,
            "max_llamadas_mes": limites["max_llamadas_mes"],
            "max_medicamentos_por_paciente": limites["max_medicamentos_por_paciente"],
        }
