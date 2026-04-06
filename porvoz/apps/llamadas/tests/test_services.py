"""
Tests para servicios de llamadas.
Ejecutar: python manage.py test apps.llamadas
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.llamadas.models import Llamada, RespuestaLlamada
from apps.llamadas.services.llamada_service import LlamadaService
from apps.medicamentos.models import Medicamento
from apps.notificaciones.models import Notificacion
from apps.pacientes.models import Paciente


class LlamadaServiceTest(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="cuidador_test",
            password="pass1234",
            email="test@test.com",
        )
        self.paciente = Paciente.objects.create(
            usuario=self.usuario,
            nombre="Juan Pérez",
            telefono="+573001234567",
        )
        self.medicamento = Medicamento.objects.create(
            paciente=self.paciente,
            nombre="Aspirina",
            dosis="100mg",
            instrucciones_llamada="Recordar tomar con agua.",
        )

    def test_crear_llamada_programada(self):
        """Crea una llamada programada con estado 'programada'."""
        fecha = timezone.now() + timedelta(hours=1)
        llamada = LlamadaService.crear_llamada_programada(
            medicamento=self.medicamento,
            usuario=self.usuario,
            paciente=self.paciente,
            fecha_programada=fecha,
        )
        self.assertIsInstance(llamada, Llamada)
        self.assertEqual(llamada.estado, Llamada.ESTADO_PROGRAMADA)
        self.assertEqual(llamada.medicamento, self.medicamento)
        self.assertEqual(llamada.paciente, self.paciente)

    def test_registrar_respuesta_atendida(self):
        """Registra respuesta atendida sin crear alerta."""
        Llamada.objects.create(
            medicamento=self.medicamento,
            paciente=self.paciente,
            usuario=self.usuario,
            fecha_programada=timezone.now(),
            call_sid="CA_test_atendida",
            estado=Llamada.ESTADO_EN_CURSO,
        )
        respuesta = LlamadaService.registrar_respuesta(
            call_sid="CA_test_atendida",
            transcripcion="Asistente: ¿Tomó el medicamento?\nUsuario: Sí, ya lo tomé.",
            como_respondio=RespuestaLlamada.RESPUESTA_ATENDIDA,
        )
        self.assertIsNotNone(respuesta)
        self.assertEqual(respuesta.como_respondio, RespuestaLlamada.RESPUESTA_ATENDIDA)
        self.assertEqual(Notificacion.objects.filter(tipo=Notificacion.TIPO_ALERTA).count(), 0)

    def test_registrar_respuesta_no_atendida_crea_alerta(self):
        """Respuesta no_atendida crea una Notificación de ALERTA."""
        Llamada.objects.create(
            medicamento=self.medicamento,
            paciente=self.paciente,
            usuario=self.usuario,
            fecha_programada=timezone.now(),
            call_sid="CA_test_no_atendida",
            estado=Llamada.ESTADO_EN_CURSO,
        )
        LlamadaService.registrar_respuesta(
            call_sid="CA_test_no_atendida",
            transcripcion="",
            como_respondio=RespuestaLlamada.RESPUESTA_NO_ATENDIDA,
        )
        alertas = Notificacion.objects.filter(
            usuario=self.usuario,
            tipo=Notificacion.TIPO_ALERTA,
        )
        self.assertEqual(alertas.count(), 1)
        self.assertIn("Aspirina", alertas.first().titulo)

    def test_registrar_respuesta_buzon_crea_alerta(self):
        """Respuesta buzon también crea alerta."""
        Llamada.objects.create(
            medicamento=self.medicamento,
            paciente=self.paciente,
            usuario=self.usuario,
            fecha_programada=timezone.now(),
            call_sid="CA_test_buzon",
            estado=Llamada.ESTADO_EN_CURSO,
        )
        LlamadaService.registrar_respuesta(
            call_sid="CA_test_buzon",
            transcripcion="",
            como_respondio=RespuestaLlamada.RESPUESTA_BUZON,
        )
        self.assertEqual(
            Notificacion.objects.filter(tipo=Notificacion.TIPO_ALERTA).count(), 1
        )

    def test_registrar_estado_final_completada(self):
        """Estado 'completed' de Twilio → Llamada.ESTADO_COMPLETADA."""
        Llamada.objects.create(
            medicamento=self.medicamento,
            paciente=self.paciente,
            usuario=self.usuario,
            fecha_programada=timezone.now(),
            call_sid="CA_test_status",
            estado=Llamada.ESTADO_EN_CURSO,
        )
        LlamadaService.registrar_estado_final("CA_test_status", "completed", duracion=45)
        llamada = Llamada.objects.get(call_sid="CA_test_status")
        self.assertEqual(llamada.estado, Llamada.ESTADO_COMPLETADA)
        self.assertEqual(llamada.duracion, 45)

    def test_registrar_estado_final_fallida(self):
        """Estado 'no-answer' de Twilio → Llamada.ESTADO_FALLIDA."""
        Llamada.objects.create(
            medicamento=self.medicamento,
            paciente=self.paciente,
            usuario=self.usuario,
            fecha_programada=timezone.now(),
            call_sid="CA_test_noanswer",
            estado=Llamada.ESTADO_EN_CURSO,
        )
        LlamadaService.registrar_estado_final("CA_test_noanswer", "no-answer")
        llamada = Llamada.objects.get(call_sid="CA_test_noanswer")
        self.assertEqual(llamada.estado, Llamada.ESTADO_FALLIDA)

    def test_registrar_respuesta_call_sid_inexistente(self):
        """call_sid que no existe retorna None sin explotar."""
        resultado = LlamadaService.registrar_respuesta(
            call_sid="CA_inexistente",
            transcripcion="",
            como_respondio=RespuestaLlamada.RESPUESTA_ATENDIDA,
        )
        self.assertIsNone(resultado)
