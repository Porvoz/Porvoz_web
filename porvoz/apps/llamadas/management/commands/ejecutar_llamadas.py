"""
Management command para ejecutar llamadas pendientes.

Uso:
    python manage.py ejecutar_llamadas          # Una sola ejecución
    python manage.py ejecutar_llamadas --loop   # Bucle continuo cada 60s

En producción, programar con cron:
    */5 * * * * cd /ruta/al/proyecto && python manage.py ejecutar_llamadas
"""

import time

from django.core.management.base import BaseCommand

from apps.llamadas.services.llamada_service import LlamadaService


class Command(BaseCommand):
    help = "Ejecuta las llamadas programadas pendientes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Ejecutar en bucle continuo cada 60 segundos.",
        )
        parser.add_argument(
            "--intervalo",
            type=int,
            default=60,
            help="Segundos entre ejecuciones en modo --loop (default: 60).",
        )

    def handle(self, *args, **options):
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
        self.stdout.write("[ejecutar_llamadas] Buscando llamadas pendientes...")
        try:
            LlamadaService.ejecutar_llamadas_pendientes()
            self.stdout.write(self.style.SUCCESS("[ejecutar_llamadas] Listo."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"[ejecutar_llamadas] Error: {e}"))
