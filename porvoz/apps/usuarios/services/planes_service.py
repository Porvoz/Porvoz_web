"""
Datos de planes, límites y verificación de cuotas.

Costo estimado por llamada (Twilio Colombia ~$0.035/min, 2 min promedio):
  ≈ $0.07 USD ≈ 260 COP por llamada

Márgenes aproximados:
  Básico    ($0):       5 llamadas →  costo ~1.300 COP  (subsidio de adquisición)
  Familiar  ($29.900):  60 llamadas → costo ~15.600 COP → ganancia ~14.300 COP/usuario
  Profesional ($89.900): 250 llamadas → costo ~65.000 COP → ganancia ~24.900 COP/usuario
"""

from datetime import date

from apps.core.models import Perfil

# ------------------------------------------------------------------
# Límites por plan
# ------------------------------------------------------------------

PLAN_LIMITS = {
    Perfil.PLAN_FREEMIUM: {
        "max_pacientes": 1,
        "max_medicamentos_por_paciente": 3,
        "max_llamadas_mes": 5,
    },
    Perfil.PLAN_GROWTH: {
        "max_pacientes": 5,
        "max_medicamentos_por_paciente": 10,
        "max_llamadas_mes": 60,
    },
    Perfil.PLAN_MULTI_BUSINESS: {
        "max_pacientes": 15,
        "max_medicamentos_por_paciente": None,  # ilimitado
        "max_llamadas_mes": 250,
    },
}

# ------------------------------------------------------------------
# Datos de planes para la UI
# ------------------------------------------------------------------

PLANES_DATA = {
    Perfil.PLAN_FREEMIUM: {
        "nombre": "Básico",
        "tagline": "Empieza sin costo. Ideal para conocer Porvoz.",
        "precio": "$0",
        "precio_cop": None,
        "precio_mensual": 0,
        "destacado": False,
        "caracteristicas": [
            "1 paciente",
            "Hasta 3 medicamentos",
            "5 llamadas automatizadas/mes",
            "Dashboard básico",
            "Historial 30 días",
        ],
        "limites": PLAN_LIMITS[Perfil.PLAN_FREEMIUM],
        "boton_texto": "Empezar gratis",
        "boton_estilo": "border-slate-700 text-slate-700 hover:bg-slate-50",
    },
    Perfil.PLAN_GROWTH: {
        "nombre": "Familiar",
        "tagline": "Para familias que cuidan a sus seres queridos.",
        "precio": "$29.900",
        "precio_cop": "29.900",
        "precio_mensual": 29900,
        "destacado": True,
        "caracteristicas": [
            "Hasta 5 pacientes",
            "Hasta 10 medicamentos por paciente",
            "60 llamadas automatizadas/mes",
            "Dashboard completo",
            "Historial 6 meses",
            "Llamadas con IA en español",
            "Alertas de adherencia",
            "Soporte por correo",
        ],
        "limites": PLAN_LIMITS[Perfil.PLAN_GROWTH],
        "boton_texto": "Contratar Familiar",
        "boton_estilo": "bg-slate-800 text-white hover:bg-slate-700",
    },
    Perfil.PLAN_MULTI_BUSINESS: {
        "nombre": "Profesional",
        "tagline": "Para clínicas, EPS y equipos de salud.",
        "precio": "$89.900",
        "precio_cop": "89.900",
        "precio_mensual": 89900,
        "destacado": False,
        "caracteristicas": [
            "Hasta 15 pacientes",
            "Medicamentos ilimitados",
            "250 llamadas automatizadas/mes",
            "Dashboard completo",
            "Historial completo",
            "Llamadas con IA en español",
            "Alertas de adherencia",
            "Reportes de adherencia",
            "Soporte prioritario",
        ],
        "limites": PLAN_LIMITS[Perfil.PLAN_MULTI_BUSINESS],
        "boton_texto": "Contratar Profesional",
        "boton_estilo": "border-slate-800 text-slate-800 hover:bg-slate-100",
    },
}


def obtener_planes(plan_actual: str | None = None) -> list[dict]:
    """Retorna la lista de planes con marca de plan actual."""
    planes = [
        {**PLANES_DATA[key], "plan_key": key}
        for key in [
            Perfil.PLAN_FREEMIUM,
            Perfil.PLAN_GROWTH,
            Perfil.PLAN_MULTI_BUSINESS,
        ]
    ]
    for plan in planes:
        plan["es_plan_actual"] = (
            plan_actual == plan["plan_key"] if plan_actual else False
        )
    return planes


# ------------------------------------------------------------------
# PlanService — verificación de cuotas
# ------------------------------------------------------------------


class PlanService:
    """Verifica límites del plan activo de un usuario."""

    @staticmethod
    def get_limites(plan: str) -> dict:
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
        limites = PlanService.get_limites(perfil.plan)
        max_l = limites["max_llamadas_mes"]
        hoy = date.today()
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
        """Retorna uso actual del usuario para mostrar en UI."""
        from apps.llamadas.models import Llamada
        from apps.medicamentos.models import Medicamento
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
