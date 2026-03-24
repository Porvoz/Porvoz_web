"""
Servicio para gestión de medicamentos.
"""
from datetime import datetime
from typing import Optional

from django.contrib.auth.models import User

from apps.medicamentos.models import Medicamento, HorarioMedicamento
from apps.pacientes.models import Paciente


class MedicamentoService:
    
    @staticmethod
    def crear_medicamento(
        paciente: Paciente,
        nombre: str,
        dosis: str,
        frecuencia_tipo: str = Medicamento.FRECUENCIA_HORARIO,
        horarios: list[str] = None,
        cada_x_horas: int = None,
        hora_inicio: str = None,
        fecha_inicio: str = None,
        duracion_dias: int = None,
        instrucciones_llamada: str = "",
        minutos_antes: int = 0,
    ) -> Medicamento:
        """Crea un medicamento con sus horarios."""
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
        )
        
        if horarios and frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO:
            for i, h in enumerate(horarios):
                if h:
                    try:
                        hora = datetime.strptime(h, "%H:%M").time()
                        HorarioMedicamento.objects.create(
                            medicamento=medicamento,
                            hora=hora,
                            orden=i
                        )
                    except ValueError:
                        pass
        
        return medicamento
    
    @staticmethod
    def actualizar_medicamento(
        medicamento: Medicamento,
        nombre: str,
        dosis: str,
        frecuencia_tipo: str = Medicamento.FRECUENCIA_HORARIO,
        horarios: list[str] = None,
        cada_x_horas: int = None,
        hora_inicio: str = None,
        fecha_inicio: str = None,
        duracion_dias: int = None,
        instrucciones_llamada: str = "",
        minutos_antes: int = 0,
    ) -> Medicamento:
        """Actualiza un medicamento con sus horarios."""
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
        medicamento.save()
        
        medicamento.horarios.all().delete()
        if horarios and frecuencia_tipo == Medicamento.FRECUENCIA_HORARIO:
            for i, h in enumerate(horarios):
                if h:
                    try:
                        hora = datetime.strptime(h, "%H:%M").time()
                        HorarioMedicamento.objects.create(
                            medicamento=medicamento,
                            hora=hora,
                            orden=i
                        )
                    except ValueError:
                        pass
        
        return medicamento
    
    @staticmethod
    def toggle_medicamento(medicamento: Medicamento) -> bool:
        """Activa/desactiva un medicamento. Retorna el nuevo estado."""
        medicamento.activo = not medicamento.activo
        medicamento.save()
        return medicamento.activo
    
    @staticmethod
    def obtener_por_id(
        paciente_id: int,
        medicamento_id: int,
        usuario: User
    ) -> Optional[Medicamento]:
        """Obtiene un medicamento verificando pertenencia."""
        try:
            return Medicamento.objects.get(
                id=medicamento_id,
                paciente__id=paciente_id,
                paciente__usuario=usuario
            )
        except Medicamento.DoesNotExist:
            return None
