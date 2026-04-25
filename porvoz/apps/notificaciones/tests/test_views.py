from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.notificaciones.models import Notificacion
from apps.pacientes.models import Paciente


class ExportNotificationsCsvViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="csv_user",
            email="csv_user@test.com",
            password="Pass12345",
        )
        self.client.login(username="csv_user", password="Pass12345")

        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre="Matias Martinez",
            telefono="+573001112233",
            es_usuario_mismo=False,
        )

    def test_export_csv_uses_utf8_bom_and_preserves_accents(self):
        Notificacion.objects.create(
            usuario=self.user,
            paciente=self.paciente,
            tipo=Notificacion.TIPO_SISTEMA,
            titulo='Medicamento "Losartan" a tiempo',
            mensaje="Notificacion con acentos: atención, corazón, presión",
            prioridad=Notificacion.PRIORIDAD_NORMAL,
        )

        response = self.client.get(reverse("export_notifications_csv"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"\xef\xbb\xbf"))

        text = response.content.decode("utf-8-sig")
        self.assertIn("Título", text)
        self.assertIn("atención", text)
        self.assertIn("presión", text)
        # Fecha exportada como texto (prefijo ') para evitar #### en Excel.
        self.assertRegex(text, r"'\d{2}/\d{2}/\d{4} \d{2}:\d{2}")
