from datetime import time, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.dashboard.services.dashboard_service import DashboardService
from apps.medicamentos.models import Medicamento
from apps.pacientes.models import Paciente


class DashboardProximasLlamadasFallbackTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dash_user",
            email="dash_user@test.com",
            password="Pass12345",
        )
        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre="Paciente Prueba",
            telefono="+573001112233",
            timezone="America/Bogota",
        )

    def test_obtener_proximas_llamadas_usa_medicamento_cuando_no_hay_llamadas_futuras(self):
        ahora_local = timezone.localtime(timezone.now())
        hora_futura = (ahora_local + timedelta(hours=1)).time().replace(second=0, microsecond=0)

        Medicamento.objects.create(
            paciente=self.paciente,
            nombre="Losartan",
            dosis="1 tableta",
            frecuencia_tipo=Medicamento.FRECUENCIA_HORARIO,
            horario=hora_futura,
            activo=True,
        )

        proximas = DashboardService.obtener_proximas_llamadas(self.user)

        self.assertEqual(len(proximas), 1)
        self.assertEqual(proximas[0].medicamento.nombre, "Losartan")
        self.assertEqual(proximas[0].paciente.nombre, "Paciente Prueba")
        self.assertGreater(proximas[0].fecha_programada, timezone.now())
