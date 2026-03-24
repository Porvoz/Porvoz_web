"""
Datos y lógica de planes de suscripción.
"""

from apps.core.models import Perfil

PLANES_DATA = {
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


def obtener_planes(plan_actual: str | None = None) -> list[dict]:
    """Retorna la lista de planes con marca de plan actual."""
    planes = [
        {**PLANES_DATA[key], "plan_key": key}
        for key in [Perfil.PLAN_FREEMIUM, Perfil.PLAN_GROWTH, Perfil.PLAN_MULTI_BUSINESS]
    ]
    for plan in planes:
        plan["es_plan_actual"] = plan_actual == plan["plan_key"] if plan_actual else False
    return planes
