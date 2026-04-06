"""
Servicio para estadísticas y datos del dashboard.
"""

from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Prefetch

from apps.core.models import Perfil
from apps.medicamentos.models import Medicamento
from apps.notificaciones.models import Notificacion
from apps.pacientes.models import Paciente


class DashboardService:

    ICONOS = {
        "alerta": "exclamation-triangle",
        "recordatorio": "bell",
        "sistema_paciente": "person-plus",
        "sistema_medicamento": "capsule",
        "sistema_condicion": "heart-pulse",
        "default": "info-circle",
    }

    @staticmethod
    def obtener_pacientes(usuario: User, ordenar: str = "recientes") -> list:
        """Obtiene pacientes ordenados según el criterio."""
        base_qs = (
            Paciente.objects.filter(usuario=usuario, activo=True)
            .select_related("usuario", "usuario__perfil")
            .prefetch_related(
                Prefetch(
                    "medicamentos", queryset=Medicamento.objects.filter(activo=True)
                ),
                "enfermedades",
            )
        )

        if ordenar == "nombre_asc":
            return list(base_qs.order_by("nombre"))
        elif ordenar == "nombre_desc":
            return list(base_qs.order_by("-nombre"))
        elif ordenar in (
            "medicamentos",
            "inicio",
            "edad_asc",
            "edad_desc",
            "condicion",
        ):
            base_list = list(base_qs)
            if ordenar == "medicamentos":
                return sorted(
                    base_list, key=lambda p: p.medicamentos.count(), reverse=True
                )
            elif ordenar == "inicio":

                def _inicio(p):
                    m = p.medicamentos.filter(activo=True).order_by("creado_en").first()
                    return m.creado_en if m else p.creado_en

                return sorted(base_list, key=_inicio, reverse=True)
            elif ordenar == "edad_asc":

                def _edad_asc(p):
                    edad = p.get_edad_display()
                    return (edad if edad is not None else 999, p.nombre)

                return sorted(base_list, key=_edad_asc)
            elif ordenar == "edad_desc":

                def _edad_desc(p):
                    edad = p.get_edad_display()
                    return (-(edad if edad is not None else 999), p.nombre)

                return sorted(base_list, key=_edad_desc)
            elif ordenar == "condicion":
                return sorted(
                    base_list,
                    key=lambda p: (
                        (p.get_primera_condicion() or "zzz").lower(),
                        p.nombre,
                    ),
                )

        return list(base_qs.order_by("-es_usuario_mismo", "-creado_en"))

    @staticmethod
    def obtener_total_medicamentos(usuario: User) -> int:
        """Obtiene el total de medicamentos activos del usuario."""
        return Medicamento.objects.filter(
            paciente__usuario=usuario, activo=True
        ).count()

    @staticmethod
    def obtener_proximos_recordatorios(usuario: User, limite: int = 5) -> list:
        """Obtiene los próximos recordatorios de medicamentos."""
        hoy = datetime.now().date()

        medicamentos = (
            Medicamento.objects.filter(
                paciente__usuario=usuario,
                activo=True,
                frecuencia_tipo=Medicamento.FRECUENCIA_HORARIO,
            )
            .prefetch_related("horarios")
            .select_related("paciente")
        )

        items = []
        for med in medicamentos:
            horarios = med.get_horarios_ordenados()
            if not horarios:
                continue
            for h in horarios:
                items.append(
                    {
                        "medicamento": med,
                        "horario": h.hora,
                        "fecha": hoy,
                    }
                )

        items.sort(key=lambda x: x["horario"])
        return items[:limite]

    @staticmethod
    def obtener_actividad_reciente(usuario: User, limite: int = 5) -> list:
        """Obtiene la actividad reciente del usuario (notificaciones)."""
        notificaciones = (
            Notificacion.objects.filter(usuario=usuario)
            .select_related("paciente", "medicamento")
            .order_by("-creado_en")[:10]
        )

        return [
            {
                "icono": DashboardService._icono_para_notificacion(n),
                "descripcion": n.titulo,
                "fecha": n.creado_en,
            }
            for n in notificaciones
        ][:limite]

    @staticmethod
    def _icono_para_notificacion(notif) -> str:
        """Mapea tipo/título de notificación a icono."""
        if notif.tipo == "alerta":
            return DashboardService.ICONOS["alerta"]
        if notif.tipo == "recordatorio":
            return DashboardService.ICONOS["recordatorio"]

        tit = notif.titulo or ""
        if "Paciente" in tit:
            return DashboardService.ICONOS["sistema_paciente"]
        if "Medicamento" in tit:
            return DashboardService.ICONOS["sistema_medicamento"]
        if "Condición" in tit:
            return DashboardService.ICONOS["sistema_condicion"]

        return DashboardService.ICONOS["default"]

    @staticmethod
    def obtener_datos_completos(usuario: User, ordenar: str = "recientes") -> dict:
        """Obtiene todos los datos necesarios para el dashboard."""
        perfil, _ = Perfil.objects.get_or_create(user=usuario)

        return {
            "perfil": perfil,
            "pacientes": DashboardService.obtener_pacientes(usuario, ordenar),
            "total_medicamentos": DashboardService.obtener_total_medicamentos(usuario),
            "proximos_recordatorios": DashboardService.obtener_proximos_recordatorios(
                usuario
            ),
            "actividad_reciente": DashboardService.obtener_actividad_reciente(usuario),
            "dias_restantes_plan": perfil.get_dias_restantes_plan(),
            "nombre_plan": perfil.get_plan_display(),
            "opciones_ordenar": [
                ("recientes", "Más recientes"),
                ("nombre_asc", "Nombre A-Z"),
                ("nombre_desc", "Nombre Z-A"),
                ("edad_desc", "Mayores primero"),
                ("edad_asc", "Menores primero"),
                ("condicion", "Por condición"),
                ("medicamentos", "Más medicamentos"),
                ("inicio", "Inicio tratamiento"),
            ],
        }
