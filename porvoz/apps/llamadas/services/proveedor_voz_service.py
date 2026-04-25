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
MSG_EMERGENCIA = (
    "Lo escucho. Por su seguridad, llame a un familiar o a su médico de inmediato. "
    "Si es una emergencia, marque el número de emergencias. Hasta luego."
)
MSG_RECHAZO    = "Entendido. Le avisaremos a su cuidador. Hasta luego."


class ProveedorVozService:
    """Integración con Twilio (llamadas) y Gemini (IA conversacional)."""

    # Re-exportados para que las views accedan a los mensajes vía el servicio.
    MSG_CONFIRMADO = MSG_CONFIRMADO
    MSG_NEGATIVO = MSG_NEGATIVO
    MSG_DESPUES = MSG_DESPUES
    MSG_NO_ESCUCHO = MSG_NO_ESCUCHO
    MSG_TIMEOUT = MSG_TIMEOUT
    MSG_EMERGENCIA = MSG_EMERGENCIA
    MSG_RECHAZO = MSG_RECHAZO

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
    def disparar_llamada(numero_telefono: str, voice_url: str, status_url: str) -> str:
        """
        Inicia una llamada con Twilio.

        - machine_detection="Enable": detecta buzón de voz de forma síncrona. Twilio
          espera hasta ~4s antes de invocar la URL de voz, y el resultado llega como
          AnsweredBy en el primer webhook de voz (sin callbacks adicionales).
        - NO usamos async_amd: envía un webhook extra al status_callback con
          AnsweredBy, que provocaba doble registro de estado y deduplicación errónea.
        - time_limit=90: corta la llamada a los 90 s máximo.
        - TWILIO_DRY_RUN=true: simula la llamada sin contactar Twilio.

        Returns:
            call_sid (str)
        """
        if os.environ.get("TWILIO_DRY_RUN", "").lower() == "true":
            import uuid
            fake_sid = f"DRY_{uuid.uuid4().hex[:16].upper()}"
            logger.info(f"[Twilio][DRY_RUN] Llamada simulada: {fake_sid} → {numero_telefono}")
            return fake_sid

        client = ProveedorVozService.get_twilio_client()
        phone_from = ProveedorVozService.get_twilio_phone()

        call = client.calls.create(
            url=voice_url,
            to=numero_telefono,
            from_=phone_from,
            status_callback=status_url,
            status_callback_method="POST",
            status_callback_event=["completed"],
            time_limit=90,
            machine_detection="Enable",
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
            _gemini_model = genai.GenerativeModel("gemini-2.0-flash-lite")
        return _gemini_model

    @staticmethod
    def generar_respuesta_ia(
        input_usuario: str,
        nombre_med: str,
        instrucciones: str = "",
        nombre_paciente: str = "",
        historial: str = "",
    ) -> str:
        """
        Genera una respuesta conversacional cuando la intención del paciente es ambigua.

        Recibe contexto completo del medicamento y paciente para responder
        de forma natural. Gemini NO lee las instrucciones en voz alta — las
        usa como contexto silencioso para entender el medicamento.
        """
        try:
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

            model = ProveedorVozService._get_gemini_model()

            contexto_med = f"Medicamento: {nombre_med}."
            if instrucciones:
                contexto_med += f" Contexto: {instrucciones}."

            nombre_display = nombre_paciente if nombre_paciente else "el paciente"

            system = (
                f"Eres Porvoz, asistente de voz para recordatorio de medicamentos. "
                f"Estás hablando con {nombre_display}. {contexto_med} "
                "Tu único objetivo es confirmar si tomó el medicamento. "
                "Responde SIEMPRE de forma natural y breve (máximo 2 oraciones, en español). "
                "Reglas estrictas que NUNCA puedes romper: "
                "1. NUNCA des consejos médicos, diagnósticos, dosis, efectos secundarios "
                "ni explicaciones de qué hace el medicamento. "
                "2. Si el paciente menciona dolor, mareo, falta de aire, sangrado, "
                "desmayo, no poder moverse, o cualquier síntoma grave: responde EXACTAMENTE "
                "'Por favor llame a un familiar o a su médico de inmediato. Hasta luego.' y nada más. "
                "3. Si pregunta sobre su salud, dolor o síntomas: responde "
                "'Le recomiendo consultarlo con su médico. Hasta luego.' "
                "4. Si dice que rechaza el tratamiento o que no quiere tomarlo más: "
                "responde 'Entendido, le avisaremos a su cuidador. Hasta luego.' y termina. "
                "5. Si confirma que lo tomó → despídete con 'Hasta luego'. "
                "6. Si dice que no lo tomó → anímalo brevemente a tomarlo y despídete. "
                "7. Si su respuesta es ambigua → pregunta directamente: '¿Ya lo tomó, sí o no?'. "
                "8. NUNCA repitas los datos personales del paciente más de una vez. "
                "9. NUNCA cambies de tema fuera del medicamento."
            )

            # Truncar historial para no inflar el prompt
            lineas_historial = historial.split("\n") if historial else []
            historial_recortado = "\n".join(lineas_historial[-8:])

            prompt = (
                f"{system}\n\n"
                f"Conversación hasta ahora:\n{historial_recortado}\n"
                f'El paciente acaba de decir: "{input_usuario}"\n'
                "Responde en máximo 2 oraciones."
            )

            # Timeout de 3.5s — si Gemini no responde, Twilio no queda colgado
            with ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(model.generate_content, prompt)
                try:
                    response = future.result(timeout=3.5)
                except FuturesTimeoutError:
                    logger.warning("[Gemini] Timeout (3.5s) — usando respuesta estática")
                    return MSG_TIMEOUT

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
            'timeout="8" speechTimeout="3" language="es-MX">\n'
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
