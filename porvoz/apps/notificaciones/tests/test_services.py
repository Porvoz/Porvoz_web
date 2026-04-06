"""
Tests para NotificacionService.
Ejecutar: python manage.py test apps.notificaciones
"""

from django.test import TestCase
from django.contrib.auth.models import User

from apps.notificaciones.models import Notificacion
from apps.notificaciones.services import NotificacionService


class NotificacionServiceCrearTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )

    def test_crear_notificacion_sistema(self):
        notif = NotificacionService.crear_notificacion_sistema(
            usuario=self.user,
            titulo="Paciente agregado",
            mensaje="Se agregó un paciente.",
        )
        self.assertEqual(notif.tipo, Notificacion.TIPO_SISTEMA)
        self.assertEqual(notif.titulo, "Paciente agregado")
        self.assertFalse(notif.leida)

    def test_crear_notificacion_recordatorio(self):
        notif = NotificacionService.crear_notificacion_recordatorio(
            usuario=self.user,
            titulo="Tomar Aspirina",
        )
        self.assertEqual(notif.tipo, Notificacion.TIPO_RECORDATORIO)

    def test_crear_notificacion_alerta(self):
        notif = NotificacionService.crear_notificacion_alerta(
            usuario=self.user,
            titulo="Medicamento no tomado",
        )
        self.assertEqual(notif.tipo, Notificacion.TIPO_ALERTA)


class NotificacionServiceLeidaTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser2",
            email="test2@test.com",
            password="testpass123",
        )
        self.notif = NotificacionService.crear_notificacion_sistema(
            usuario=self.user,
            titulo="Test",
        )

    def test_marcar_como_leida(self):
        resultado = NotificacionService.marcar_como_leida(self.notif.id, self.user)
        self.assertTrue(resultado)
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.leida)

    def test_marcar_como_no_leida(self):
        self.notif.leida = True
        self.notif.save()
        resultado = NotificacionService.marcar_como_no_leida(self.notif.id, self.user)
        self.assertTrue(resultado)
        self.notif.refresh_from_db()
        self.assertFalse(self.notif.leida)

    def test_marcar_todas_como_leidas(self):
        NotificacionService.crear_notificacion_sistema(usuario=self.user, titulo="Otra")
        count = NotificacionService.marcar_todas_como_leidas(self.user)
        self.assertEqual(count, 2)
        no_leidas = Notificacion.objects.filter(usuario=self.user, leida=False).count()
        self.assertEqual(no_leidas, 0)

    def test_marcar_id_inexistente_retorna_false(self):
        resultado = NotificacionService.marcar_como_leida(99999, self.user)
        self.assertFalse(resultado)


class NotificacionServiceEliminarTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser3",
            email="test3@test.com",
            password="testpass123",
        )

    def test_eliminar_notificacion(self):
        notif = NotificacionService.crear_notificacion_sistema(
            usuario=self.user, titulo="Para eliminar"
        )
        resultado = NotificacionService.eliminar_notificacion(notif.id, self.user)
        self.assertTrue(resultado)
        self.assertFalse(Notificacion.objects.filter(id=notif.id).exists())

    def test_eliminar_notificacion_inexistente(self):
        resultado = NotificacionService.eliminar_notificacion(99999, self.user)
        self.assertFalse(resultado)

    def test_eliminar_multiples(self):
        n1 = NotificacionService.crear_notificacion_sistema(
            usuario=self.user, titulo="N1"
        )
        n2 = NotificacionService.crear_notificacion_sistema(
            usuario=self.user, titulo="N2"
        )
        count = NotificacionService.eliminar_notificaciones([n1.id, n2.id], self.user)
        self.assertEqual(count, 2)


class NotificacionServiceFiltrosTest(TestCase):
    def test_filtros_desde_dict_tipo(self):
        datos = {"tipo": "recordatorio", "solo_no_leidas": "1"}
        filtros = NotificacionService.obtener_filtros_desde_dict(datos)
        self.assertEqual(filtros["tipo"], "recordatorio")
        self.assertTrue(filtros["solo_no_leidas"])

    def test_filtros_desde_dict_none_string(self):
        datos = {"tipo": "None", "paciente": "None"}
        filtros = NotificacionService.obtener_filtros_desde_dict(datos)
        self.assertIsNone(filtros["tipo"])
        self.assertIsNone(filtros["paciente_id"])

    def test_estadisticas(self):
        user = User.objects.create_user(username="stats_user", password="pass")
        NotificacionService.crear_notificacion_sistema(usuario=user, titulo="N1")
        NotificacionService.crear_notificacion_sistema(usuario=user, titulo="N2")
        NotificacionService.marcar_como_leida(
            Notificacion.objects.filter(usuario=user).first().id, user
        )
        stats = NotificacionService.obtener_estadisticas(user)
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["no_leidas"], 1)
