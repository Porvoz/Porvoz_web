"""
Servicio para gestión de medicamentos.
"""

from datetime import datetime
from typing import Optional

from django.contrib.auth.models import User

from apps.medicamentos.models import HorarioMedicamento, Medicamento
from apps.pacientes.models import Paciente


class MedicamentoService:

    @staticmethod
    def crear_medicamento(
        paciente: Paciente,
        nombre: str,
        dosis: str,
        frecuencia_tipo: str = Medicamento.FRECUENCIA_HORARIO,
        horarios: list = None,
        cada_x_horas: int = None,
        hora_inicio: str = None,
        fecha_inicio: str = None,
        duracion_dias: int = None,
        instrucciones_llamada: str = "",
        minutos_antes: int = 0,
        max_reintentos: int = 1,
        minutos_entre_reintentos: int = 30,
    ) -> Medicamento:
        """Crea un medicamento con sus horarios."""
        horario_legacy, fecha_inicio_date = MedicamentoService._parsear_campos(
            horarios, frecuencia_tipo, fecha_inicio
        )
        medicamento = Medicamento.objects.create(
            paciente=paciente,
            nombre=nombre,
            dosis=dosis,
            frecuencia_tipo=frecuencia_tipo,
            horario=horario_legacy,
            cada_x_horas=cada_x_horas,
            hora_inicio=hora_inicio,
            fecha_inicio_tratamiento=fecha_inicio_date,
            duracion_dias=duracion_dias,
            instrucciones_llamada=instrucciones_llamada,
            minutos_antes_llamada=minutos_antes,
            max_reintentos=max_reintentos,
            minutos_entre_reintentos=minutos_entre_reintentos,
        )
        MedicamentoService._guardar_horarios(medicamento, horarios, frecuencia_tipo)
        return medicamento

    @staticmethod
    def actualizar_medicamento(
        medicamento: Medicamento,
        nombre: str,
        dosis: str,
        frecuencia_tipo: str = Medicamento.FRECUENCIA_HORARIO,
        horarios: list = None,
        cada_x_horas: int = None,
        hora_inicio: str = None,
        fecha_inicio: str = None,
        duracion_dias: int = None,
        instrucciones_llamada: str = "",
        minutos_antes: int = 0,
        max_reintentos: int = 1,
        minutos_entre_reintentos: int = 30,
    ) -> Medicamento:
        """Actualiza un medicamento con sus horarios."""
        horario_legacy, fecha_inicio_date = MedicamentoService._parsear_campos(
            horarios, frecuencia_tipo, fecha_inicio
        )
        medicamento.nombre = nombre
        medicamento.dosis = dosis
        medicamento.frecuencia_tipo = frecuencia_tipo
        medicamento.horario = horario_legacy
        medicamento.cada_x_horas = cada_x_horas
        medicamento.hora_inicio = hora_inicio
        medicamento.fecha_inicio_tratamiento = fecha_inicio_date
        medicamento.duracion_dias = duracion_dias
        medicamento.instrucciones_llamada = instrucciones_llamada
        medicamento.minutos_antes_llamada = minutos_antes
        medicamento.max_reintentos = max_reintentos
        medicamento.minutos_entre_reintentos = minutos_entre_reintentos
        medicamento.save()

        medicamento.horarios.all().delete()
        MedicamentoService._guardar_horarios(medicamento, horarios, frecuencia_tipo)
        return medicamento

    @staticmethod
    def toggle_medicamento(medicamento: Medicamento) -> bool:
        """Activa/desactiva un medicamento. Retorna el nuevo estado."""
        medicamento.activo = not medicamento.activo
        medicamento.save()
        return medicamento.activo

    @staticmethod
    def obtener_por_id(
        paciente_id: int, medicamento_id: int, usuario: User
    ) -> Optional[Medicamento]:
        """Obtiene un medicamento verificando pertenencia. Retorna None si no existe."""
        try:
            return Medicamento.objects.get(
                id=medicamento_id, paciente__id=paciente_id, paciente__usuario=usuario
            )
        except Medicamento.DoesNotExist:
            return None

    # ------------------------------------------------------------------
    # Privados
    # ------------------------------------------------------------------

    @staticmethod
    def _parsear_campos(horarios, frecuencia_tipo, fecha_inicio):
        """Parsea horario legacy y fecha de inicio desde strings."""
        horario_legacy = None
        if horarios and frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO:
            try:
                horario_legacy = datetime.strptime(horarios[0], "%H:%M").time()
            except ValueError:
                pass

        fecha_inicio_date = None
        if fecha_inicio:
            try:
                fecha_inicio_date = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            except ValueError:
                pass

        return horario_legacy, fecha_inicio_date

    @staticmethod
    def _guardar_horarios(medicamento, horarios, frecuencia_tipo):
        """Crea los objetos HorarioMedicamento a partir de la lista de strings."""
        if not horarios or frecuencia_tipo != Medicamento.FRECUENCIA_HORARIO:
            return
        for i, h in enumerate(horarios):
            if h:
                try:
                    hora = datetime.strptime(h, "%H:%M").time()
                    HorarioMedicamento.objects.create(
                        medicamento=medicamento, hora=hora, orden=i
                    )
                except ValueError:
                    pass
