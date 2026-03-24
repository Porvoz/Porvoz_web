import logging
import os
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)
_scheduler = None


def process_pending_reminders():

    from django.utils import timezone
    from reminders.models import Reminder
    from calls.models import CallRecord

    now = timezone.now()
    print("AHORA:", now)

    due = Reminder.objects.filter(
        status="pending",
        scheduled_at__lte=now
    ).select_related("contact")

    if not due.exists():
        return

    logger.info(f"[Scheduler] {now.isoformat()} — {due.count()} recordatorio(s) por disparar")

    base_url = _get_base_url()

    for reminder in due:

        if not reminder.contact or not reminder.contact.phone:
            logger.warning(f"[Scheduler] Recordatorio #{reminder.id} sin número")
            Reminder.objects.filter(pk=reminder.id).update(status="failed")
            continue

        try:

            from ai.twilio_gemini import get_twilio_client, get_twilio_phone
            import urllib.parse

            client = get_twilio_client()
            phone = get_twilio_phone()

            logger.info(
                f"[Scheduler] Llamando a {reminder.contact.name} ({reminder.contact.phone})"
            )

            call = client.calls.create(

                url=f"{base_url}/api/calls/webhook/voice?reminderId={reminder.id}&message={urllib.parse.quote(reminder.message or '')}",

                to=reminder.contact.phone,

                from_=phone,

                status_callback=f"{base_url}/api/calls/webhook/status",

                status_callback_method="POST",

            )

            CallRecord.objects.create(
                reminder=reminder,
                contact=reminder.contact,
                call_sid=call.sid,
                status="initiated",
            )

            Reminder.objects.filter(pk=reminder.id).update(status="called")

            logger.info(f"[Scheduler] Llamada iniciada: {call.sid}")

        except Exception as e:

            logger.error(f"[Scheduler] Error llamando recordatorio #{reminder.id}: {e}")

            CallRecord.objects.create(
                reminder=reminder,
                contact=reminder.contact,
                call_sid=None,
                status="failed",
            )

            Reminder.objects.filter(pk=reminder.id).update(status="failed")


# ---------------------------------------------------
# URL PUBLICA PARA TWILIO
# ---------------------------------------------------

def _get_base_url():

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


# ---------------------------------------------------
# SCHEDULER
# ---------------------------------------------------

def start_scheduler():

    global _scheduler

    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler(
        timezone=ZoneInfo("America/Bogota")
    )

    _scheduler.add_job(
        process_pending_reminders,
        trigger="interval",
        seconds=30,
        id="check_reminders",
        replace_existing=True,
    )

    _scheduler.start()

    logger.info(
        "[Scheduler] Iniciado — revisando recordatorios cada 30 segundos"
    )