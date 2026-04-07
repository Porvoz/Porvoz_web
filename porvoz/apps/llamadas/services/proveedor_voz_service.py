"""
Servicio para integración con Twilio y Gemini.

Responsabilidades:
- Disparar llamadas via Twilio
- Generar respuestas de IA via Gemini (solo cuando la intención del paciente es ambigua)
- Construir TwiML (XML que Twilio ejecuta)

Diseño de costos:
- Saludo y cierres con intención clara → TwiML estático (0 llamadas a Gemini)
- Solo llama a Gemini cuando el paciente dice algo ambiguo
- Esto reduce el uso de Gemini a ~20% de las llamadas
"""

import html
import logging
import os

logger = logging.getLogger(__name__)

_twilio_client = None
_twilio_phone = None
_gemini_model = None

# Respuestas deterministas — sin IA, sin costo extra
MSG_CONFIRMADO = "Perfecto, qué bueno. Que tenga un buen día. Hasta luego."
MSG_NEGATIVO   = "Entendido. Recuerde tomar su medicamento a la brevedad. Hasta luego."
MSG_DESPUES    = "Entendido, le llamaremos más tarde. Hasta luego."
MSG_NO_ESCUCHO = "No pude escucharle. Recuerde tomar su medicamento. Hasta luego."
MSG_TIMEOUT    = "Llamada finalizada. Recuerde tomar su medicamento. Hasta luego."


class ProveedorVozService:
    """Integración con Twilio (llamadas) y Gemini (IA conversacional)."""

    # ------------------------------------------------------------------
    # Twilio — cliente y número
    # ------------------------------------------------------------------

    @staticmethod
    def get_twilio_client():
        global _twilio_client
        if _twilio_client is None:
            account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
            auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
            if not account_sid or not auth_token:
                raise RuntimeError(
                    "TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN son obligatorios"
                )
            from twilio.rest import Client
            _twilio_client = Client(account_sid, auth_token)
        return _twilio_client

    @staticmethod
    def get_twilio_phone():
        global _twilio_phone
        if _twilio_phone is None:
            import re
            # Soporta tanto TWILIO_FROM_NUMBER (preferido) como TWILIO_PHONE_NUMBER (legado)
            numero = (
                os.environ.get("TWILIO_FROM_NUMBER")
                or os.environ.get("TWILIO_PHONE_NUMBER", "")
            ).strip()
            if re.match(r"^\+\d{7,15}$", numero):
                _twilio_phone = numero
            else:
                match = re.search(r"\+\d{7,15}", numero)
                if match:
                    _twilio_phone = match.group(0)
                else:
                    raise RuntimeError(
                        "TWILIO_FROM_NUMBER no es válido (ej: +16056746999)"
                    )
        return _twilio_phone

    @staticmethod
    def disparar_llamada(numero_telefono: str, mensaje: str, voice_url: str, status_url: str) -> str:
        """
        Inicia una llamada con Twilio.

        - machine_detection="Enable": detecta buzón de voz automáticamente.
        - time_limit=90: corta la llamada a los 90 s (máx ~2 turnos de conversación).

        Returns:
            call_sid (str)
        """
        client = ProveedorVozService.get_twilio_client()
        phone_from = ProveedorVozService.get_twilio_phone()

        call = client.calls.create(
            url=voice_url,
            to=numero_telefono,
            from_=phone_from,
            status_callback=status_url,
            status_callback_method="POST",
            time_limit=90,  # corta a los 90 s si la conversación no cierra
        )
        logger.info(f"[Twilio] Llamada iniciada: {call.sid} → {numero_telefono}")
        return call.sid

    # ------------------------------------------------------------------
    # Gemini — solo para respuestas ambiguas
    # ------------------------------------------------------------------

    @staticmethod
    def _get_gemini_model():
        global _gemini_model
        if _gemini_model is None:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY es obligatoria")
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # gemini-2.0-flash-lite: modelo más barato y rápido disponible
            _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        return _gemini_model

    @staticmethod
    def generar_respuesta_ia(input_usuario: str, mensaje_recordatorio: str, historial: str = "") -> str:
        """
        Genera una respuesta para el caso en que el paciente dijo algo ambiguo.
        Solo se llama cuando la detección por palabras clave no fue concluyente.

        Restricciones del modelo:
        - Máximo 1 oración de respuesta
        - Sin datos personales
        - Sin consejos médicos
        - Siempre termina con despedida si la intención es clara
        """
        try:
            model = ProveedorVozService._get_gemini_model()

            # Prompt compacto: menos tokens = más barato y más rápido
            system = (
                "Eres Porvoz, asistente de recordatorio de medicamentos. "
                "Responde en UNA oración máximo. "
                "Nunca pidas datos personales ni des consejos médicos. "
                "Si el paciente confirma o niega claramente, despídete con 'Hasta luego'."
            )

            if not historial:
                # No debería ocurrir (el saludo ahora es estático), pero por seguridad
                prompt = (
                    f"{system}\n\n"
                    f"Recordatorio: {mensaje_recordatorio}\n"
                    "Pregunta si ya tomó el medicamento. Una oración."
                )
            else:
                prompt = (
                    f"{system}\n\n"
                    f"Recordatorio: {mensaje_recordatorio}\n"
                    f"Conversación:\n{historial}\n"
                    f'Paciente dijo: "{input_usuario}"\n'
                    "Responde en una oración. Si confirma o niega, despídete."
                )

            response = model.generate_content(prompt)
            text = getattr(response, "text", "")
            if not text:
                return MSG_TIMEOUT

            # Limitar a ~200 chars (~30 palabras habladas ≈ 8 segundos de audio)
            return text.strip()[:200]

        except Exception as e:
            logger.error(f"[Gemini] Error: {e}")
            return MSG_TIMEOUT

    # ------------------------------------------------------------------
    # TwiML builders
    # ------------------------------------------------------------------

    @staticmethod
    def _escape(text: str) -> str:
        return html.escape(text, quote=True)

    @staticmethod
    def build_twiml_saludo(instrucciones: str, gather_url: str) -> str:
        """
        TwiML del saludo inicial — completamente estático, sin Gemini.
        Construye el mensaje directamente desde las instrucciones del medicamento.
        """
        mensaje = f"Hola, le llama Porvoz. {instrucciones} ¿Ya lo tomó?"
        return ProveedorVozService.build_twiml_gather(mensaje, gather_url)

    @staticmethod
    def build_twiml_gather(mensaje: str, gather_url: str) -> str:
        """TwiML que habla y espera respuesta del paciente."""
        msg    = ProveedorVozService._escape(mensaje)
        action = ProveedorVozService._escape(gather_url)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>\n"
            f'  <Gather input="speech" action="{action}" method="POST" '
            'timeout="5" speechTimeout="2" language="es-MX">\n'
            f'    <Say language="es-MX" voice="Polly.Mia">{msg}</Say>\n'
            "  </Gather>\n"
            # Si no se escuchó nada después del timeout → cierre estático
            f'  <Say language="es-MX" voice="Polly.Mia">'
            f'{ProveedorVozService._escape(MSG_NO_ESCUCHO)}'
            "</Say>\n"
            "  <Hangup/>\n"
            "</Response>"
        )

    # Alias para compatibilidad con código existente
    @staticmethod
    def build_twiml_inicio(mensaje: str, gather_url: str) -> str:
        return ProveedorVozService.build_twiml_gather(mensaje, gather_url)

    @staticmethod
    def build_twiml_continuar(mensaje: str, gather_url: str) -> str:
        return ProveedorVozService.build_twiml_gather(mensaje, gather_url)

    @staticmethod
    def build_twiml_fin(mensaje: str) -> str:
        """TwiML que reproduce mensaje y cuelga. Sin más interacción."""
        msg = ProveedorVozService._escape(mensaje)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>\n"
            f'  <Say language="es-MX" voice="Polly.Mia">{msg}</Say>\n'
            "  <Hangup/>\n"
            "</Response>"
        )

    # ------------------------------------------------------------------
    # URL base
    # ------------------------------------------------------------------

    @staticmethod
    def get_base_url() -> str:
        base = os.environ.get("TWILIO_BASE_URL") or os.environ.get("BASE_URL")
        if base:
            return base.rstrip("/")
        dominios = os.environ.get("REPLIT_DOMAINS", "")
        primer_dominio = dominios.split(",")[0].strip() if dominios else ""
        if primer_dominio:
            return f"https://{primer_dominio}"
        return f"http://localhost:{os.environ.get('PORT', '8000')}"
