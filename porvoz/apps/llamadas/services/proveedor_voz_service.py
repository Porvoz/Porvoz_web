"""
Servicio para integración con Twilio y Gemini.

Responsabilidades:
- Disparar llamadas via Twilio
- Generar respuestas de IA via Gemini
- Construir TwiML (XML que Twilio ejecuta)
"""

import html
import logging
import os

logger = logging.getLogger(__name__)

_twilio_client = None
_twilio_phone = None
_gemini_model = None


class ProveedorVozService:
    """Integración con Twilio (llamadas) y Gemini (IA conversacional)."""

    # ------------------------------------------------------------------
    # Twilio
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

            numero = os.environ.get("TWILIO_PHONE_NUMBER", "")
            numero = numero.strip()
            if re.match(r"^\+\d{7,15}$", numero):
                _twilio_phone = numero
            else:
                match = re.search(r"\+\d{7,15}", numero)
                if match:
                    _twilio_phone = match.group(0)
                else:
                    raise RuntimeError(
                        "TWILIO_PHONE_NUMBER no es un número válido (ej: +573001234567)"
                    )
        return _twilio_phone

    @staticmethod
    def disparar_llamada(numero_telefono, mensaje, voice_url, status_url):
        """
        Inicia una llamada con Twilio.

        Args:
            numero_telefono: Número del paciente (ej: +573001234567)
            mensaje: Mensaje del recordatorio (para el webhook)
            voice_url: URL pública del webhook /llamadas/webhook/voice/
            status_url: URL pública del webhook /llamadas/webhook/status/

        Returns:
            call_sid (str) — ID de la llamada en Twilio
        """
        client = ProveedorVozService.get_twilio_client()
        phone_from = ProveedorVozService.get_twilio_phone()

        call = client.calls.create(
            url=voice_url,
            to=numero_telefono,
            from_=phone_from,
            status_callback=status_url,
            status_callback_method="POST",
        )
        logger.info(f"[Twilio] Llamada iniciada: {call.sid} → {numero_telefono}")
        return call.sid

    # ------------------------------------------------------------------
    # Gemini
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
            _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        return _gemini_model

    @staticmethod
    def generar_respuesta_ia(input_usuario, mensaje_recordatorio, historial=""):
        """
        Genera una respuesta conversacional usando Gemini.

        Args:
            input_usuario: Lo que dijo el paciente en este turno
            mensaje_recordatorio: El recordatorio original del medicamento
            historial: Historial de la conversación hasta ahora

        Returns:
            respuesta (str)
        """
        try:
            model = ProveedorVozService._get_gemini_model()
            system_prompt = (
                "Eres un asistente de salud de Porvoz. Tu tarea es recordar al paciente "
                "que debe tomar su medicamento. Habla de forma cálida, breve y clara. "
                "Responde en español. Si el paciente confirma, despídete amablemente. "
                "Si no confirma o hay duda, recuérdale amablemente."
            )

            if not historial:
                prompt = (
                    f"{system_prompt}\n\n"
                    f"Recordatorio: {mensaje_recordatorio}\n\n"
                    "Saluda, preséntate como Porvoz y da el recordatorio. "
                    "Luego pregunta si ya tomó el medicamento."
                )
            else:
                prompt = (
                    f"{system_prompt}\n\n"
                    f"Recordatorio original: {mensaje_recordatorio}\n\n"
                    f"Historial:\n{historial}\n\n"
                    f'El paciente acaba de decir: "{input_usuario}"\n\n'
                    "Responde de forma natural y breve."
                )

            response = model.generate_content(prompt)
            text = getattr(response, "text", None)
            if not text:
                return (
                    f"Hola, le llamo de Porvoz para recordarle: {mensaje_recordatorio}. "
                    "¿Ya lo tomó?"
                )
            return text.strip()

        except Exception as e:
            logger.error(f"[Gemini] Error generando respuesta: {e}")
            return (
                f"Hola, le llamo de Porvoz para recordarle: {mensaje_recordatorio}. "
                "¿Ya tomó su medicamento?"
            )

    # ------------------------------------------------------------------
    # TwiML builders
    # ------------------------------------------------------------------

    @staticmethod
    def _escape(text):
        return html.escape(text, quote=True)

    @staticmethod
    def build_twiml_inicio(mensaje, gather_url):
        """TwiML para el inicio de la llamada: habla y espera respuesta."""
        msg = ProveedorVozService._escape(mensaje)
        action = ProveedorVozService._escape(gather_url)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>\n"
            f'  <Gather input="speech" action="{action}" method="POST" '
            'timeout="6" speechTimeout="auto" language="es-MX">\n'
            f'    <Say language="es-MX" voice="Polly.Mia">{msg}</Say>\n'
            "  </Gather>\n"
            '  <Say language="es-MX" voice="Polly.Mia">'
            "No pude escucharle. Recuerde tomar su medicamento. Que tenga un buen día."
            "</Say>\n"
            "  <Hangup/>\n"
            "</Response>"
        )

    @staticmethod
    def build_twiml_continuar(mensaje, gather_url):
        """TwiML para continuar la conversación."""
        return ProveedorVozService.build_twiml_inicio(mensaje, gather_url)

    @staticmethod
    def build_twiml_fin(mensaje):
        """TwiML para terminar la llamada."""
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
    def get_base_url():
        """Retorna la URL base pública (para construir URLs de webhooks)."""
        base = os.environ.get("TWILIO_BASE_URL") or os.environ.get("BASE_URL")
        if base:
            return base.rstrip("/")
        dominios = os.environ.get("REPLIT_DOMAINS", "")
        primer_dominio = dominios.split(",")[0].strip() if dominios else ""
        if primer_dominio:
            return f"https://{primer_dominio}"
        port = os.environ.get("PORT", "8000")
        return f"http://localhost:{port}"
