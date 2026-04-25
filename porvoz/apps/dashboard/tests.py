"""
Tests for dashboard app (stats, activity feed, call metrics).
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Perfil
from apps.dashboard.services.dashboard_service import DashboardService
from apps.pacientes.models import Paciente
from apps.medicamentos.models import Medicamento
from apps.notificaciones.models import Notificacion
from apps.llamadas.models import Llamada, RespuestaLlamada


class DashboardServiceTest(TestCase):
    """Tests for dashboard statistics and data aggregation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="TestPass123"
        )
        Perfil.objects.create(user=self.user)

        self.patient = Paciente.objects.create(
            usuario=self.user,
            nombre="John Doe",
            telefono="+573001234567"
        )

        self.med = Medicamento.objects.create(
            paciente=self.patient,
            nombre="Aspirina",
            dosis="500mg",
            frecuencia_tipo="diario"
        )

    def test_obtener_datos_completos(self):
        """Should aggregate dashboard data correctly."""
        datos = DashboardService.obtener_datos_completos(self.user)

        self.assertEqual(len(datos['pacientes']), 1)
        self.assertEqual(datos['pacientes'][0].nombre, "John Doe")
        self.assertEqual(datos['total_medicamentos'], 1)

    def test_estadisticas_llamadas_semana(self):
        """Should calculate call stats for the week."""
        ayer = timezone.now() - timedelta(days=1)
        call = Llamada.objects.create(
            usuario=self.user,
            paciente=self.patient,
            medicamento=self.med,
            fecha_programada=ayer,
            estado=Llamada.ESTADO_COMPLETADA
        )

        RespuestaLlamada.objects.create(
            llamada=call,
            como_respondio=RespuestaLlamada.RESPUESTA_ATENDIDA,
            resultado=RespuestaLlamada.RESULTADO_CONFIRMADA
        )

        datos = DashboardService.obtener_datos_completos(self.user)

        self.assertGreater(datos['llamadas_semana'], 0)
        self.assertGreater(datos['llamadas_atendidas_semana'], 0)

    def test_actividad_reciente(self):
        """Should retrieve recent activity (notifications)."""
        Notificacion.objects.create(
            usuario=self.user,
            titulo="Test Alert",
            tipo=Notificacion.TIPO_ALERTA,
            prioridad=Notificacion.PRIORIDAD_NORMAL
        )

        datos = DashboardService.obtener_datos_completos(self.user)

        self.assertGreater(len(datos['actividad_reciente']), 0)
