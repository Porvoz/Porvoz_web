"""
Servicio para integración con proveedores de voz.

Soporta múltiples proveedores (Twilio, Vonage, etc.)
Se configura vía variables de entorno (VOICE_PROVIDER).
"""


class ProveedorVozService:
    """
    Abstracción para proveedores de voz.

    Interfaz genérica que permite cambiar proveedores sin afectar el resto del código.
    """

    @staticmethod
    def disparar_llamada(numero_telefono, instrucciones_ai, callback_url):
        """
        Dispara una llamada automática a través del proveedor configurado.

        Args:
            numero_telefono: Número del paciente (ej: +573001234567)
            instrucciones_ai: Prompt/contexto para la IA (ej: "Recordar Aspirina 100mg")
            callback_url: URL para webhook de respuesta (privada, autenticada)

        Returns:
            (success: bool, external_call_id: str, error_msg: Optional[str])
        """
        # TODO: Implementar en Sprint 2
        pass

    @staticmethod
    def obtener_estado_llamada(external_call_id):
        """
        Consulta el estado de una llamada en el proveedor.

        Args:
            external_call_id: ID externo de la llamada

        Returns:
            estado: "en_curso" | "completada" | "fallida"
        """
        # TODO: Implementar en Sprint 2
        pass

    @staticmethod
    def procesar_webhook_respuesta(data_webhook):
        """
        Procesa la respuesta de webhook del proveedor.

        Args:
            data_webhook: Data JSON del webhook (estructura depende del proveedor)

        Returns:
            (tipo_respuesta: str, transcripcion: str, duracion_segundos: int)
        """
        # TODO: Implementar en Sprint 2
        pass
