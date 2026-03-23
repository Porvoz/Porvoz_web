"""
Servicio para gestión de notificaciones.
"""
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q

from apps.notificaciones.models import Notificacion


class NotificacionService:

    @staticmethod
    def crear_notificacion_sistema(
        usuario: User,
        titulo: str,
        mensaje: str = "",
        paciente=None,
        medicamento=None,
    ) -> Notificacion:
        """Crea una notificación de tipo sistema."""
        return Notificacion.objects.create(
            usuario=usuario,
            paciente=paciente,
            medicamento=medicamento,
            tipo=Notificacion.TIPO_SISTEMA,
            titulo=titulo,
            mensaje=mensaje,
        )

    @staticmethod
    def crear_notificacion_recordatorio(
        usuario: User,
        titulo: str,
        mensaje: str = "",
        paciente=None,
        medicamento=None,
        fecha_programada: datetime = None,
    ) -> Notificacion:
        """Crea una notificación de tipo recordatorio."""
        return Notificacion.objects.create(
            usuario=usuario,
            paciente=paciente,
            medicamento=medicamento,
            tipo=Notificacion.TIPO_RECORDATORIO,
            titulo=titulo,
            mensaje=mensaje,
            fecha_programada=fecha_programada,
        )

    @staticmethod
    def crear_notificacion_alerta(
        usuario: User,
        titulo: str,
        mensaje: str = "",
        paciente=None,
        medicamento=None,
    ) -> Notificacion:
        """Crea una notificación de tipo alerta."""
        return Notificacion.objects.create(
            usuario=usuario,
            paciente=paciente,
            medicamento=medicamento,
            tipo=Notificacion.TIPO_ALERTA,
            titulo=titulo,
            mensaje=mensaje,
        )

    @staticmethod
    def marcar_como_leida(notificacion_id: int, usuario: User) -> bool:
        """Marca una notificación como leída. Retorna True si se encontró."""
        try:
            notif = Notificacion.objects.get(id=notificacion_id, usuario=usuario)
            notif.leida = True
            notif.save()
            return True
        except Notificacion.DoesNotExist:
            return False

    @staticmethod
    def marcar_como_no_leida(notificacion_id: int, usuario: User) -> bool:
        """Marca una notificación como no leída. Retorna True si se encontró."""
        try:
            notif = Notificacion.objects.get(id=notificacion_id, usuario=usuario)
            notif.leida = False
            notif.save()
            return True
        except Notificacion.DoesNotExist:
            return False

    @staticmethod
    def marcar_todas_como_leidas(usuario: User) -> int:
        """Marca todas las notificaciones como leídas. Retorna cantidad."""
        return Notificacion.objects.filter(
            usuario=usuario,
            leida=False
        ).update(leida=True)

    @staticmethod
    def eliminar_notificacion(notificacion_id: int, usuario: User) -> bool:
        """Elimina una notificación. Retorna True si se encontró."""
        deleted, _ = Notificacion.objects.filter(
            id=notificacion_id,
            usuario=usuario
        ).delete()
        return deleted > 0

    @staticmethod
    def eliminar_notificaciones(ids: list[int], usuario: User) -> int:
        """Elimina múltiples notificaciones. Retorna cantidad eliminada."""
        deleted, _ = Notificacion.objects.filter(
            id__in=ids,
            usuario=usuario
        ).delete()
        return deleted

    @staticmethod
    def obtener_filtros_desde_dict(datos: dict) -> dict:
        """Extrae filtros desde un diccionario de parámetros.

        Args:
            datos: Dict con claves como 'paciente', 'tipo', 'fecha_desde', etc.

        Returns:
            Dict normalizado con los filtros procesados.
        """
        paciente_id = datos.get("paciente") or None
        if paciente_id == "None":
            paciente_id = None

        tipo = datos.get("tipo") or None
        if tipo == "None":
            tipo = None

        fecha_desde = datos.get("fecha_desde")
        fecha_hasta = datos.get("fecha_hasta")
        solo_no_leidas = datos.get("solo_no_leidas") == "1"
        buscar = (datos.get("buscar") or "").strip()

        return {
            "paciente_id": paciente_id,
            "tipo": tipo,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "solo_no_leidas": solo_no_leidas,
            "buscar": buscar,
        }

    @staticmethod
    def aplicar_filtros(queryset, filtros: dict):
        """Aplica filtros a un queryset de notificaciones."""
        if filtros.get("paciente_id"):
            queryset = queryset.filter(paciente_id=filtros["paciente_id"])

        if filtros.get("tipo"):
            queryset = queryset.filter(tipo=filtros["tipo"])

        if filtros.get("fecha_desde"):
            try:
                fecha = datetime.strptime(filtros["fecha_desde"], "%Y-%m-%d").date()
                queryset = queryset.filter(creado_en__date__gte=fecha)
            except ValueError:
                pass

        if filtros.get("fecha_hasta"):
            try:
                fecha = datetime.strptime(filtros["fecha_hasta"], "%Y-%m-%d").date()
                queryset = queryset.filter(creado_en__date__lte=fecha)
            except ValueError:
                pass

        if filtros.get("solo_no_leidas"):
            queryset = queryset.filter(leida=False)

        if filtros.get("buscar"):
            queryset = queryset.filter(
                Q(titulo__icontains=filtros["buscar"]) |
                Q(mensaje__icontains=filtros["buscar"])
            )

        return queryset

    @staticmethod
    def obtener_estadisticas(usuario: User) -> dict:
        """Obtiene estadísticas de notificaciones para un usuario."""
        base_qs = Notificacion.objects.filter(usuario=usuario)

        return {
            "total": base_qs.count(),
            "no_leidas": base_qs.filter(leida=False).count(),
        }
