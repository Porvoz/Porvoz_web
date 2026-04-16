"""
Servicio para estadísticas y datos del dashboard.
"""

from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.utils import timezone

from apps.core.models import Perfil
from apps.llamadas.models import Llamada, RespuestaLlamada
from apps.medicamentos.models import Medicamento
from apps.notificaciones.models import Notificacion
from apps.pacientes.models import Paciente
from apps.usuarios.services.perfil_service import PerfilService


class DashboardService:

    ICONOS = {
        "alerta": "exclamation-triangle",
        "llamada_ok": "telephone-fill",
        "llamada": "telephone",
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
        """
        Obtiene los recordatorios de medicamentos para hoy.
        Incluye frecuencia horario fijo y cada X horas.
        Adjunta el estado de la última llamada ejecutada hoy para cada medicamento.
        """
        from apps.llamadas.models import Llamada, RespuestaLlamada

        ahora = timezone.now()
        hoy = timezone.localtime(ahora).date()
        inicio_hoy = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
        fin_hoy = inicio_hoy + timedelta(hours=24)

        medicamentos = (
            Medicamento.objects.filter(
                paciente__usuario=usuario,
                activo=True,
            )
            .prefetch_related("horarios")
            .select_related("paciente")
        )

        items = []
        for med in medicamentos:
            if med.frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO:
                horarios = med.get_horarios_ordenados()
                if not horarios:
                    continue
                for h in horarios:
                    items.append({
                        "medicamento": med,
                        "horario": h.hora,
                        "fecha": hoy,
                    })

            elif med.frecuencia_tipo == Medicamento.FRECUENCIA_CADA_X_HORAS:
                if not med.hora_inicio or not med.cada_x_horas:
                    continue
                dt_base = timezone.make_aware(datetime.combine(hoy, med.hora_inicio))
                intervalo = timedelta(hours=med.cada_x_horas)
                # Próxima toma que no haya pasado aún
                dt_siguiente = dt_base
                while dt_siguiente <= ahora:
                    dt_siguiente += intervalo
                # Solo mostrar si es hoy
                if timezone.localtime(dt_siguiente).date() == hoy:
                    items.append({
                        "medicamento": med,
                        "horario": timezone.localtime(dt_siguiente).time(),
                        "fecha": hoy,
                    })

        # Adjuntar estado de la última llamada ejecutada hoy para cada medicamento
        for item in items:
            llamada_hoy = (
                Llamada.objects.filter(
                    medicamento=item["medicamento"],
                    fecha_programada__gte=inicio_hoy,
                    fecha_programada__lt=fin_hoy,
                    estado__in=[Llamada.ESTADO_COMPLETADA, Llamada.ESTADO_FALLIDA],
                )
                .select_related("respuesta")
                .order_by("-fecha_programada")
                .first()
            )
            item["llamada_hoy"] = llamada_hoy

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
        if notif.tipo == "llamada":
            tit = notif.titulo or ""
            if "confirmada" in tit.lower():
                return DashboardService.ICONOS["llamada_ok"]
            return DashboardService.ICONOS["llamada"]

        tit = notif.titulo or ""
        if "Paciente" in tit:
            return DashboardService.ICONOS["sistema_paciente"]
        if "Medicamento" in tit or "medicamento" in tit:
            return DashboardService.ICONOS["sistema_medicamento"]
        if "Condición" in tit:
            return DashboardService.ICONOS["sistema_condicion"]

        return DashboardService.ICONOS["default"]

    @staticmethod
    def obtener_alertas_activas(usuario: User, limite: int = 3) -> list:
        """Últimas alertas no leídas para mostrar en el banner del dashboard."""
        return list(
            Notificacion.objects.filter(
                usuario=usuario,
                leida=False,
                tipo=Notificacion.TIPO_ALERTA,
            )
            .select_related("paciente", "medicamento")
            .order_by("-creado_en")[:limite]
        )

    @staticmethod
    def obtener_proximas_llamadas(usuario: User, limite: int = 5) -> list:
        """Próximas llamadas programadas (aún no ejecutadas) del usuario."""
        ahora = timezone.now()
        return list(
            Llamada.objects.filter(
                usuario=usuario,
                estado=Llamada.ESTADO_PROGRAMADA,
                fecha_programada__gte=ahora,
            )
            .select_related("medicamento", "paciente")
            .order_by("fecha_programada")[:limite]
        )

    @staticmethod
    def obtener_estadisticas_llamadas(usuario: User) -> dict:
        """Estadísticas de llamadas de los últimos 7 días."""
        hace_7_dias = timezone.now() - timedelta(days=7)
        qs = Llamada.objects.filter(
            usuario=usuario,
            fecha_programada__gte=hace_7_dias,
            estado__in=[Llamada.ESTADO_COMPLETADA, Llamada.ESTADO_FALLIDA],
        )
        total = qs.count()
        atendidas = qs.filter(
            respuesta__como_respondio=RespuestaLlamada.RESPUESTA_ATENDIDA
        ).count()
        adherencia = round((atendidas / total * 100) if total > 0 else 0)
        return {
            "llamadas_semana": total,
            "llamadas_atendidas_semana": atendidas,
            "llamadas_no_atendidas_semana": total - atendidas,
            "adherencia_semana": adherencia,
        }

    @staticmethod
    def obtener_datos_completos(usuario: User, ordenar: str = "recientes") -> dict:
        """Obtiene todos los datos necesarios para el dashboard."""
        perfil, _ = Perfil.objects.get_or_create(user=usuario)
        pacientes = DashboardService.obtener_pacientes(usuario, ordenar)
        stats_llamadas = DashboardService.obtener_estadisticas_llamadas(usuario)

        return {
            "perfil": perfil,
            "pacientes": pacientes,
            "total_medicamentos": DashboardService.obtener_total_medicamentos(usuario),
            "proximos_recordatorios": DashboardService.obtener_proximos_recordatorios(
                usuario
            ),
            "alertas_activas": DashboardService.obtener_alertas_activas(usuario),
            "proximas_llamadas": DashboardService.obtener_proximas_llamadas(usuario),
            "actividad_reciente": DashboardService.obtener_actividad_reciente(usuario),
            "dias_restantes_plan": PerfilService.get_dias_restantes_plan(perfil),
            "nombre_plan": perfil.get_plan_display(),
            "pacientes_sin_medicamentos": [
                p for p in pacientes if p.medicamentos.count() == 0
            ],
            **stats_llamadas,
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
