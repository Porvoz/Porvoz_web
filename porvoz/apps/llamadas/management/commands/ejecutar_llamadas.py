"""
Management command para ejecutar llamadas pendientes.

Uso:
    python manage.py ejecutar_llamadas          # Una sola ejecución
    python manage.py ejecutar_llamadas --loop   # Bucle continuo (dev sin Celery)

En producción con Celery, usar el beat scheduler en vez de este comando:
    celery -A config beat --loglevel=info
    celery -A config worker --loglevel=info

En dev sin Celery:
    python manage.py ejecutar_llamadas --loop --intervalo 60
"""

import os
import time
from datetime import date, timedelta

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError

from apps.llamadas.services.llamada_service import LlamadaService

# Clave + TTL del lock que impide que dos schedulers corran en paralelo.
# TTL > intervalo máximo para que un ciclo colgado no deje el lock vivo para siempre.
_LOCK_KEY = "ejecutar_llamadas:lock"
_LOCK_TTL = 180  # 3 minutos — un ciclo nunca debería tardar más


def _celery_disponible() -> bool:
    try:
        from django.conf import settings
        return bool(getattr(settings, "CELERY_BROKER_URL", None))
    except Exception:
        return False


def _validar_base_url(stdout, style):
    """Valida que TWILIO_BASE_URL esté configurado antes de ejecutar llamadas."""
    dry_run = os.environ.get("TWILIO_DRY_RUN", "").lower() == "true"
    base_url = os.environ.get("TWILIO_BASE_URL") or os.environ.get("BASE_URL", "")

    if dry_run:
        stdout.write(style.WARNING("[ejecutar_llamadas] TWILIO_DRY_RUN=true — llamadas simuladas, no se contacta Twilio."))
        return True

    if not base_url or base_url.startswith("http://localhost"):
        raise CommandError(
            "\n[ejecutar_llamadas] ERROR: TWILIO_BASE_URL no está configurado o apunta a localhost.\n"
            "Twilio no puede enviar webhooks a localhost. Configura ngrok:\n"
            "  1. python ngrok_run.py  (en otra terminal)\n"
            "  2. Copia la URL https://xxxx.ngrok.io y ponla en .env como TWILIO_BASE_URL\n"
            "  3. Reinicia este comando.\n"
            "  O usa TWILIO_DRY_RUN=true para simular sin Twilio."
        )
    return True


class Command(BaseCommand):
    help = "Ejecuta las llamadas programadas pendientes (dev). En prod usar Celery beat."

    def add_arguments(self, parser):
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Ejecutar en bucle continuo cada N segundos (solo dev sin Celery).",
        )
        parser.add_argument(
            "--intervalo",
            type=int,
            default=60,
            help="Segundos entre ejecuciones en modo --loop (default: 60).",
        )

    def handle(self, *args, **options):
        _validar_base_url(self.stdout, self.style)

        if _celery_disponible():
            self.stdout.write(
                self.style.WARNING(
                    "[ejecutar_llamadas] Celery está configurado — "
                    "usa 'celery -A config beat' en producción. "
                    "Continuando ejecución directa para testing."
                )
            )

        if options["loop"]:
            intervalo = options["intervalo"]
            self.stdout.write(
                f"[ejecutar_llamadas] Modo bucle — cada {intervalo}s. Ctrl+C para salir."
            )
            while True:
                self._ejecutar()
                time.sleep(intervalo)
        else:
            self._ejecutar()

    def _ejecutar(self):
        # Lock distribuido: solo un proceso debe ejecutar llamadas a la vez.
        # cache.add() es atómico: si la clave ya existe, retorna False.
        pid = os.getpid()
        if not cache.add(_LOCK_KEY, pid, timeout=_LOCK_TTL):
            holder = cache.get(_LOCK_KEY)
            self.stdout.write(self.style.WARNING(
                f"[ejecutar_llamadas] Otro proceso ({holder}) tiene el lock; saltando ciclo."
            ))
            return

        try:
            # Limpiar llamadas que quedaron en en_curso por más de 10 min (webhook no llegó)
            try:
                n = LlamadaService.limpiar_llamadas_vencidas()
                if n:
                    self.stdout.write(self.style.WARNING(f"[ejecutar_llamadas] {n} llamada(s) vencida(s) limpiadas."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"[ejecutar_llamadas] Error limpiando vencidas: {e}"))

            self.stdout.write("[ejecutar_llamadas] Buscando llamadas pendientes...")
            try:
                LlamadaService.ejecutar_llamadas_pendientes()
                self.stdout.write(self.style.SUCCESS("[ejecutar_llamadas] Listo."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"[ejecutar_llamadas] Error: {e}"))

            # Notificar tratamientos que terminan mañana
            try:
                self._notificar_fin_tratamientos()
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"[ejecutar_llamadas] Error en notif. fin tratamiento: {e}"))
        finally:
            # Liberar el lock sin importar qué pasó — pero solo si somos los dueños.
            if cache.get(_LOCK_KEY) == pid:
                cache.delete(_LOCK_KEY)

    def _notificar_fin_tratamientos(self):
        """Crea notificaciones para medicamentos cuyo tratamiento termina mañana."""
        from apps.medicamentos.models import Medicamento
        from apps.notificaciones.models import Notificacion
        from apps.notificaciones.services import NotificacionService

        manana = date.today() + timedelta(days=1)
        meds = (
            Medicamento.objects.filter(activo=True, duracion_dias__isnull=False)
            .select_related("paciente", "paciente__usuario")
            .exclude(duracion_dias=0)
        )
        for med in meds:
            if not med.fecha_inicio_tratamiento or not med.duracion_dias:
                continue
            fin = med.fecha_inicio_tratamiento + timedelta(days=med.duracion_dias)
            if fin != manana:
                continue
            # Evitar duplicar: verificar que no existe ya notificación de este tipo hoy
            ya_notificado = Notificacion.objects.filter(
                usuario=med.paciente.usuario,
                medicamento=med,
                tipo=Notificacion.TIPO_ALERTA,
                titulo__icontains="termina mañana",
                creado_en__date=date.today(),
            ).exists()
            if ya_notificado:
                continue
            NotificacionService.crear_notificacion(
                usuario=med.paciente.usuario,
                tipo=Notificacion.TIPO_ALERTA,
                titulo=f'Tratamiento de "{med.nombre}" para {med.paciente.get_display_nombre()} termina mañana',
                mensaje=f"El tratamiento de {med.duracion_dias} días concluye el {fin.strftime('%d/%m/%Y')}. Verifica si debe renovarse.",
                paciente=med.paciente,
                medicamento=med,
                prioridad=Notificacion.PRIORIDAD_URGENTE,
            )
            self.stdout.write(self.style.WARNING(
                f"[ejecutar_llamadas] Notif. fin tratamiento: {med.nombre} ({med.paciente.get_display_nombre()})"
            ))
