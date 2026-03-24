"""
Servicio para gestión de llamadas automáticas.

Responsabilidades:
- Crear llamadas programadas desde medicamentos
- Ejecutar/disparar llamadas automáticas
- Registrar respuestas del usuario
- Crear alertas si la respuesta es negativa
"""


class LlamadaService:
    """Encapsula la lógica de llamadas automáticas."""

    @staticmethod
    def crear_llamada_programada(medicamento, usuario, paciente, fecha_programada):
        """
        Crea una llamada programada para un medicamento.

        Args:
            medicamento: Modelo Medicamento con instrucciones
            usuario: Usuario (cuidador)
            paciente: Paciente que debe tomar el medicamento
            fecha_programada: Fecha/hora exacta de la llamada

        Returns:
            Llamada (creada pero no ejecutada)
        """
        # TODO: Implementar en Sprint 2
        pass

    @staticmethod
    def ejecutar_llamada_automatica(llamada_id):
        """
        Ejecuta una llamada automática (dispara a proveedor de voz).

        Args:
            llamada_id: ID de Llamada a ejecutar

        Returns:
            (success: bool, external_call_id: str)
        """
        # TODO: Implementar en Sprint 2
        pass

    @staticmethod
    def registrar_respuesta(llamada_id, tipo_respuesta, duracion_segundos=0, transcripcion=""):
        """
        Registra la respuesta del usuario a una llamada.

        Args:
            llamada_id: ID de Llamada
            tipo_respuesta: "confirmada" | "negada" | "no_respondio" | "error"
            duracion_segundos: Duración de la llamada
            transcripcion: Transcripción de la llamada (opcional)

        Returns:
            RespuestaLlamada (creada)
        """
        # TODO: Implementar en Sprint 2
        pass

    @staticmethod
    def crear_alerta_si_respuesta_negativa(respuesta_llamada):
        """
        Si la respuesta fue "negada" o "no_respondio", crea una Notificacion de ALERTA.

        Args:
            respuesta_llamada: Modelo RespuestaLlamada

        Returns:
            Notificacion (si aplica) o None
        """
        # TODO: Implementar en Sprint 2
        pass
