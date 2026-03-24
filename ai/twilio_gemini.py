import os
import html

_twilio_client = None
_twilio_phone = None
_gemini_model = None


# -----------------------------
# TWILIO CLIENT
# -----------------------------
def get_twilio_client():
    global _twilio_client

    if _twilio_client is None:
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

        if not account_sid or not auth_token:
            raise RuntimeError(
                "Las variables TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN son obligatorias"
            )

        from twilio.rest import Client

        _twilio_client = Client(account_sid, auth_token)

    return _twilio_client


# -----------------------------
# TWILIO PHONE
# -----------------------------
def get_twilio_phone():
    global _twilio_phone

    if _twilio_phone is None:
        import re

        candidates = [
            os.environ.get("TWILIO_PHONE_NUMBER"),
            os.environ.get("TWILIO_FROM_NUMBER"),
        ]

        for candidate in candidates:
            if candidate:
                candidate = candidate.strip()

                if re.match(r"^\+\d{7,15}$", candidate):
                    _twilio_phone = candidate
                    return _twilio_phone

                match = re.search(r"\+\d{7,15}", candidate)
                if match:
                    _twilio_phone = match.group(0)
                    return _twilio_phone

        raise RuntimeError(
            "No se encontró un número de Twilio válido en TWILIO_PHONE_NUMBER o TWILIO_FROM_NUMBER"
        )

    return _twilio_phone


# -----------------------------
# GEMINI MODEL
# -----------------------------
def _get_gemini_model():
    global _gemini_model

    if _gemini_model is None:
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("La variable GEMINI_API_KEY es obligatoria")

        import google.generativeai as genai

        genai.configure(api_key=api_key)

        _gemini_model = genai.GenerativeModel("gemini-2.5-flash")

    return _gemini_model


# -----------------------------
# GENERATE AI RESPONSE
# -----------------------------
def generate_ai_response(user_input: str, reminder_message: str, conversation_history: str) -> str:

    try:
        model = _get_gemini_model()

        system_prompt = f"""
Eres un asistente telefónico humano de Porvoz.

Estás hablando por teléfono con una persona para recordarle algo.

Recordatorio: "{reminder_message}"

REGLAS IMPORTANTES:
- Habla como una persona real.
- Mantén respuestas cortas (máximo 2 frases).
- Siempre habla en español.
- Mantén una conversación natural.
- Después de responder, pregunta si ya realizó la acción del recordatorio.
- Si el usuario confirma que sí, agradécele y despídete.
- Si dice que no, recuérdale amablemente que lo haga.
"""

        # inicio de llamada
        if not user_input:

            prompt = f"""
{system_prompt}

La persona acaba de contestar el teléfono.

Saluda, preséntate brevemente como Porvoz y da el recordatorio.
Luego pregúntale si ya realizó la acción.
"""

        else:

            prompt = f"""
{system_prompt}

Historial:
{conversation_history}

El usuario acaba de decir:
"{user_input}"

Responde de forma natural.
"""

        response = model.generate_content(prompt)

        text = getattr(response, "text", None)

        if not text:
            return f"Hola, le llamo de Porvoz para recordarle: {reminder_message}. ¿Ya realizó esta acción?"

        return text.strip()

    except Exception as e:

        print("[Gemini ERROR]", e)

        return f"Hola, le llamo de Porvoz para recordarle: {reminder_message}. ¿Ya realizó esta acción?"

# -----------------------------
# XML ESCAPE
# -----------------------------
def _escape_xml(text: str) -> str:
    return html.escape(text, quote=True)


# -----------------------------
# TWIML WITH GATHER
# -----------------------------
def build_twiml(message: str, gather_action: str) -> str:

    safe_msg = _escape_xml(message)
    safe_action = _escape_xml(gather_action)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="{safe_action}" method="POST" timeout="6" speechTimeout="auto" language="es-MX">
    <Say language="es-MX" voice="Polly.Mia">{safe_msg}</Say>
  </Gather>

  <Say language="es-MX" voice="Polly.Mia">
  No pude escucharle. Recuerde el recordatorio. Que tenga un buen día.
  </Say>

  <Hangup/>
</Response>
"""


# -----------------------------
# FINAL TWIML
# -----------------------------
def build_end_twiml(message: str) -> str:

    safe_msg = _escape_xml(message)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="es-MX" voice="Polly.Mia">{safe_msg}</Say>
  <Hangup/>
</Response>
"""


# -----------------------------
# BASE URL
# -----------------------------
def get_base_url() -> str:

    base = os.environ.get("TWILIO_BASE_URL")

    if base:
        return base.rstrip("/")

    if os.environ.get("BASE_URL"):
        return os.environ["BASE_URL"].rstrip("/")

    domains = os.environ.get("REPLIT_DOMAINS", "")
    first_domain = domains.split(",")[0].strip() if domains else ""

    if first_domain:
        return f"https://{first_domain}"

    port = os.environ.get("PORT", "8000")

    return f"http://localhost:{port}"