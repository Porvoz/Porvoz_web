from django.core.management.base import BaseCommand

from apps.admin_panel.models import ConfiguracionPlan
from apps.core.models import Perfil


class Command(BaseCommand):
    help = "Inicializa la tabla ConfiguracionPlan con valores por defecto"

    def handle(self, *args, **options):
        planes_defaults = {
            Perfil.PLAN_FREEMIUM: {
                "nombre": "Gratuito",
                "descripcion": "Prueba Porvoz sin costo",
                "precio_mensual": 0,
                "costo_estimado": 1200,
                "limite_pacientes": 1,
                "limite_medicamentos": 2,
                "limite_llamadas_mes": 15,
            },
            Perfil.PLAN_GROWTH: {
                "nombre": "Básico",
                "descripcion": "Un paciente bajo control total",
                "precio_mensual": 24900,
                "costo_estimado": 7200,
                "limite_pacientes": 1,
                "limite_medicamentos": 5,
                "limite_llamadas_mes": 90,
            },
            Perfil.PLAN_MULTI_BUSINESS: {
                "nombre": "Familiar",
                "descripcion": "Cuida a toda la familia desde un solo lugar",
                "precio_mensual": 59900,
                "costo_estimado": 24000,
                "limite_pacientes": 4,
                "limite_medicamentos": None,
                "limite_llamadas_mes": 300,
            },
            Perfil.PLAN_PROFESIONAL: {
                "nombre": "Profesional",
                "descripcion": "Para cuidadores independientes y equipos de salud",
                "precio_mensual": 139900,
                "costo_estimado": 72000,
                "limite_pacientes": 10,
                "limite_medicamentos": None,
                "limite_llamadas_mes": 900,
            },
        }

        for plan_key, datos in planes_defaults.items():
            config, creado = ConfiguracionPlan.objects.get_or_create(
                plan=plan_key,
                defaults=datos
            )
            if creado:
                self.stdout.write(
                    self.style.SUCCESS(f"[OK] Creado: {config.nombre}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"[EXISTS] Ya existe: {config.nombre}")
                )

        self.stdout.write(self.style.SUCCESS("\n[OK] Inicializacion completada"))
