"""
Tests para los servicios del core (PerfilService, RegistroService, TelefonoService).
Ejecutar: python manage.py test apps.core
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from apps.autenticacion.services import RegistroService
from apps.core.models import Perfil
from apps.shared.services import TelefonoService
from apps.usuarios.services import PerfilService


class PerfilServiceValidarEdadTest(TestCase):
    def test_edad_valida(self):
        fecha = (date.today() - timedelta(days=365 * 25)).strftime("%Y-%m-%d")
        resultado, error = PerfilService.validar_edad(fecha)
        self.assertIsNotNone(resultado)
        self.assertIsNone(error)

    def test_edad_menor_a_10(self):
        fecha = (date.today() - timedelta(days=365 * 5)).strftime("%Y-%m-%d")
        resultado, error = PerfilService.validar_edad(fecha)
        self.assertIsNone(resultado)
        self.assertIn("10 años", error)

    def test_fecha_vacia_retorna_none(self):
        resultado, error = PerfilService.validar_edad("")
        self.assertIsNone(resultado)
        self.assertIsNone(error)

    def test_fecha_invalida_retorna_error(self):
        resultado, error = PerfilService.validar_edad("no-es-fecha")
        self.assertIsNone(resultado)
        self.assertIsNotNone(error)


class PerfilServiceCambiarPlanTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testplan",
            email="plan@test.com",
            password="testpass123",
        )
        self.perfil = Perfil.objects.create(user=self.user)

    def test_cambiar_plan_valido(self):
        ok, error = PerfilService.cambiar_plan(self.perfil, Perfil.PLAN_GROWTH)
        self.assertTrue(ok)
        self.assertIsNone(error)
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.plan, Perfil.PLAN_GROWTH)

    def test_cambiar_plan_invalido(self):
        ok, error = PerfilService.cambiar_plan(self.perfil, "plan_inexistente")
        self.assertFalse(ok)
        self.assertIsNotNone(error)

    def test_cambiar_plan_actualiza_expiracion(self):
        PerfilService.cambiar_plan(self.perfil, Perfil.PLAN_GROWTH)
        self.perfil.refresh_from_db()
        hoy = date.today()
        self.assertEqual(self.perfil.plan_expiration, hoy + timedelta(days=365))


class RegistroServiceTest(TestCase):
    def test_crear_usuario_y_perfil(self):
        user, perfil = RegistroService.crear_usuario_y_perfil(
            username="nuevo_usuario",
            email="nuevo@test.com",
            password="password123",
            first_name="Juan",
            last_name="Pérez",
        )
        self.assertIsNotNone(user.id)
        self.assertIsNotNone(perfil.id)
        self.assertEqual(perfil.user, user)
        self.assertEqual(perfil.first_name, "Juan")

    def test_crear_usuario_plan_expiracion_365_dias(self):
        user, perfil = RegistroService.crear_usuario_y_perfil(
            username="otro_usuario",
            email="otro@test.com",
            password="password123",
            first_name="Ana",
            last_name="López",
        )
        esperado = date.today() + timedelta(days=365)
        self.assertEqual(perfil.plan_expiration, esperado)


class TelefonoServiceTest(TestCase):
    def test_formatear_completo(self):
        resultado = TelefonoService.formatear_completo("+57", "3001234567")
        self.assertIn("3001234567", resultado)

    def test_formatear_completo_vacio(self):
        resultado = TelefonoService.formatear_completo("+57", "")
        self.assertEqual(resultado, "")

    def test_parsear_telefono_con_prefijo(self):
        parsed = TelefonoService.parsear_telefono("+573001234567")
        self.assertIsNotNone(parsed)

    def test_parsear_telefono_vacio(self):
        parsed = TelefonoService.parsear_telefono("")
        self.assertIsNotNone(parsed)
