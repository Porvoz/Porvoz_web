from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from apps.llamadas.models import RespuestaLlamada, Llamada
from apps.llamadas.services.llamada_service import LlamadaService
from apps.llamadas.views import _append_asistente, _detectar_resultado
from apps.medicamentos.models import Medicamento
from apps.pacientes.models import Paciente


class WebhookDecisionLogicTest(TestCase):
    def test_detectar_resultado_si_ahora_es_despues(self):
        resultado = _detectar_resultado("si ahora")
        self.assertEqual(resultado, RespuestaLlamada.RESULTADO_DESPUES)

    def test_detectar_resultado_no_simple_es_negativa(self):
        resultado = _detectar_resultado("no")
        self.assertEqual(resultado, RespuestaLlamada.RESULTADO_NEGATIVA)

    def test_detectar_resultado_confirmada_clara(self):
        resultado = _detectar_resultado("si lo tome")
        self.assertEqual(resultado, RespuestaLlamada.RESULTADO_CONFIRMADA)

    def test_append_asistente_agrega_linea(self):
        historial = "Asistente: Hola\nUsuario: si"
        final = _append_asistente(historial, "Perfecto, hasta luego")
        self.assertIn("Asistente: Perfecto, hasta luego", final)


class WebhookStatusFinalizationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="status_user",
            email="status_user@test.com",
            password="Pass12345",
        )
        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre="Paciente Estado",
            telefono="+573001112233",
        )
        self.medicamento = Medicamento.objects.create(
            paciente=self.paciente,
            nombre="Losartan",
            dosis="1 tableta",
        )
        self.llamada = Llamada.objects.create(
            usuario=self.user,
            paciente=self.paciente,
            medicamento=self.medicamento,
            fecha_programada=timezone.now(),
            estado=Llamada.ESTADO_EN_CURSO,
            call_sid="CA_status_test",
        )

    def test_estado_intermedio_no_cambia_llamada(self):
        LlamadaService.registrar_estado_final("CA_status_test", "ringing")
        self.llamada.refresh_from_db()
        self.assertEqual(self.llamada.estado, Llamada.ESTADO_EN_CURSO)
