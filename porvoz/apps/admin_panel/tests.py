"""
Tests for admin panel models, services, and views.
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.admin_panel.models import (
    CodigoAcceso,
    ConfiguracionPlan,
    MensajeTicket,
    PagoHistorico,
    TicketSoporte,
)
from apps.admin_panel.services import CodigoService
from apps.core.models import Perfil


class AdminPanelSetupMixin:
    """Shared setup for admin panel tests."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_test", password="testpass123", is_staff=True
        )
        Perfil.objects.create(user=self.admin, plan=Perfil.PLAN_FREEMIUM)

        self.user = User.objects.create_user(
            username="user_test", password="testpass123"
        )
        Perfil.objects.create(user=self.user, plan=Perfil.PLAN_FREEMIUM)

        self.client = Client()


# ---------------------------------------------------------------------------
# Modelo CodigoAcceso
# ---------------------------------------------------------------------------

class CodigoAccesoModelTest(AdminPanelSetupMixin, TestCase):

    def test_generar_codigo_formato(self):
        codigo = CodigoAcceso.generar_codigo()
        self.assertTrue(codigo.startswith("PROMO-"))
        self.assertEqual(len(codigo), 16)  # PROMO-XXXXXX-XXX

    def test_codigos_generados_son_unicos(self):
        codigos = {CodigoAcceso.generar_codigo() for _ in range(10)}
        self.assertEqual(len(codigos), 10)

    def test_estado_inicial_disponible(self):
        codigo = CodigoAcceso.objects.create(
            codigo=CodigoAcceso.generar_codigo(),
            plan=Perfil.PLAN_GROWTH,
            duracion_meses=1,
            creado_por=self.admin,
        )
        self.assertEqual(codigo.estado, CodigoAcceso.ESTADO_DISPONIBLE)

    def test_str_representation(self):
        codigo = CodigoAcceso.objects.create(
            codigo="PROMO-TEST01-ABC",
            plan=Perfil.PLAN_GROWTH,
            duracion_meses=1,
            creado_por=self.admin,
        )
        self.assertIn("PROMO-TEST01-ABC", str(codigo))
        self.assertIn("disponible", str(codigo))


# ---------------------------------------------------------------------------
# Servicio CodigoService
# ---------------------------------------------------------------------------

class CodigoServiceTest(AdminPanelSetupMixin, TestCase):

    def _crear_codigo(self, plan=Perfil.PLAN_GROWTH, duracion=1, **kwargs):
        return CodigoAcceso.objects.create(
            codigo=CodigoAcceso.generar_codigo(),
            plan=plan,
            duracion_meses=duracion,
            creado_por=self.admin,
            **kwargs,
        )

    def test_aplicar_codigo_activa_plan(self):
        codigo = self._crear_codigo()
        ok, msg = CodigoService.aplicar_codigo(self.user, codigo.codigo)
        self.assertTrue(ok)
        self.user.perfil.refresh_from_db()
        self.assertEqual(self.user.perfil.plan, Perfil.PLAN_GROWTH)
        self.assertEqual(self.user.perfil.plan_estado, Perfil.ESTADO_ACTIVO)

    def test_aplicar_codigo_marca_como_usado(self):
        codigo = self._crear_codigo()
        CodigoService.aplicar_codigo(self.user, codigo.codigo)
        codigo.refresh_from_db()
        self.assertEqual(codigo.estado, CodigoAcceso.ESTADO_USADO)
        self.assertEqual(codigo.usuario_usado_por, self.user)

    def test_aplicar_codigo_crea_pago_historico(self):
        codigo = self._crear_codigo()
        CodigoService.aplicar_codigo(self.user, codigo.codigo)
        self.assertTrue(
            PagoHistorico.objects.filter(
                usuario=self.user, tipo_pago=PagoHistorico.TIPO_CODIGO
            ).exists()
        )

    def test_aplicar_codigo_inexistente(self):
        ok, msg = CodigoService.aplicar_codigo(self.user, "PROMO-NOEXISTE-XXX")
        self.assertFalse(ok)
        self.assertIn("no encontrado", msg.lower())

    def test_aplicar_codigo_ya_usado(self):
        codigo = self._crear_codigo()
        CodigoService.aplicar_codigo(self.user, codigo.codigo)
        ok, msg = CodigoService.aplicar_codigo(self.admin, codigo.codigo)
        self.assertFalse(ok)
        self.assertIn("ya fue utilizado", msg.lower())

    def test_aplicar_codigo_expirado_por_fecha_limite(self):
        ayer = date.today() - timedelta(days=1)
        codigo = self._crear_codigo(fecha_limite_canje=ayer)
        ok, msg = CodigoService.aplicar_codigo(self.user, codigo.codigo)
        self.assertFalse(ok)
        self.assertIn("expiró", msg.lower())
        codigo.refresh_from_db()
        self.assertEqual(codigo.estado, CodigoAcceso.ESTADO_EXPIRADO)

    def test_aplicar_codigo_insensible_mayusculas(self):
        codigo = self._crear_codigo()
        ok, _ = CodigoService.aplicar_codigo(self.user, codigo.codigo.lower())
        self.assertTrue(ok)

    def test_expirar_codigos_vencidos(self):
        ayer = date.today() - timedelta(days=1)
        self._crear_codigo(fecha_limite_canje=ayer)
        self._crear_codigo(fecha_limite_canje=ayer)
        count = CodigoService.expirar_codigos_vencidos()
        self.assertEqual(count, 2)
        self.assertEqual(
            CodigoAcceso.objects.filter(estado=CodigoAcceso.ESTADO_EXPIRADO).count(), 2
        )

    def test_expirar_no_afecta_codigos_vigentes(self):
        manana = date.today() + timedelta(days=1)
        self._crear_codigo(fecha_limite_canje=manana)
        count = CodigoService.expirar_codigos_vencidos()
        self.assertEqual(count, 0)


# ---------------------------------------------------------------------------
# Modelo ConfiguracionPlan
# ---------------------------------------------------------------------------

class ConfiguracionPlanTest(TestCase):

    def _crear_config(self, precio=50000, costo=20000):
        return ConfiguracionPlan.objects.create(
            plan=Perfil.PLAN_GROWTH,
            nombre="Básico",
            precio_mensual=precio,
            costo_estimado=costo,
            limite_pacientes=3,
            limite_llamadas_mes=90,
        )

    def test_margen_neto(self):
        config = self._crear_config(precio=50000, costo=20000)
        self.assertEqual(config.margen_neto(), 30000)

    def test_porcentaje_margen(self):
        config = self._crear_config(precio=50000, costo=25000)
        self.assertEqual(config.porcentaje_margen(), 50.0)

    def test_margen_freemium_es_cero(self):
        config = ConfiguracionPlan.objects.create(
            plan=Perfil.PLAN_FREEMIUM,
            nombre="Gratuito",
            precio_mensual=0,
            costo_estimado=5000,
            limite_pacientes=1,
            limite_llamadas_mes=15,
        )
        self.assertEqual(config.margen_neto(), 0)
        self.assertEqual(config.porcentaje_margen(), 0)

    def test_str_incluye_nombre_y_precio(self):
        config = self._crear_config(precio=50000)
        self.assertIn("Básico", str(config))
        self.assertIn("50", str(config))  # número presente, formato depende del locale


# ---------------------------------------------------------------------------
# Modelo PagoHistorico
# ---------------------------------------------------------------------------

class PagoHistoricoTest(AdminPanelSetupMixin, TestCase):

    def test_costo_estimado_calculado_al_guardar(self):
        pago = PagoHistorico.objects.create(
            usuario=self.user,
            plan=Perfil.PLAN_GROWTH,
            duracion_meses=1,
            tipo_pago=PagoHistorico.TIPO_CODIGO,
            monto=50000,
            fecha_hasta=date.today() + timedelta(days=30),
        )
        self.assertIsNotNone(pago.costo_estimado)
        self.assertGreater(int(pago.costo_estimado), 0)

    def test_ganancia_neta_calculada(self):
        pago = PagoHistorico.objects.create(
            usuario=self.user,
            plan=Perfil.PLAN_GROWTH,
            duracion_meses=1,
            tipo_pago=PagoHistorico.TIPO_TRANSFERENCIA,
            monto=100000,
            fecha_hasta=date.today() + timedelta(days=30),
        )
        self.assertIsNotNone(pago.ganancia_neta)

    def test_ganancia_negativa_sin_monto(self):
        pago = PagoHistorico.objects.create(
            usuario=self.user,
            plan=Perfil.PLAN_GROWTH,
            duracion_meses=1,
            tipo_pago=PagoHistorico.TIPO_GRATUITO,
            fecha_hasta=date.today() + timedelta(days=30),
        )
        self.assertLess(int(pago.ganancia_neta), 0)


# ---------------------------------------------------------------------------
# Modelo TicketSoporte
# ---------------------------------------------------------------------------

class TicketSoporteTest(AdminPanelSetupMixin, TestCase):

    def test_estado_inicial_abierto(self):
        ticket = TicketSoporte.objects.create(
            usuario=self.user,
            titulo="Problema con llamadas",
            descripcion="No recibo llamadas",
        )
        self.assertEqual(ticket.estado, TicketSoporte.ESTADO_ABIERTO)

    def test_remitente_usuario_registrado(self):
        self.user.first_name = "Juan"
        self.user.last_name = "Pérez"
        self.user.save()
        ticket = TicketSoporte.objects.create(
            usuario=self.user,
            titulo="Test",
            descripcion="Desc",
        )
        self.assertIn("Juan", ticket.remitente)

    def test_remitente_visitante_anonimo(self):
        ticket = TicketSoporte.objects.create(
            nombre_contacto="Visitante X",
            email_contacto="visitante@test.com",
            titulo="Consulta",
            descripcion="Pregunta",
        )
        self.assertEqual(ticket.remitente, "Visitante X")
        self.assertEqual(ticket.email_remitente, "visitante@test.com")

    def test_mensaje_ticket(self):
        ticket = TicketSoporte.objects.create(
            usuario=self.user,
            titulo="Ticket con mensaje",
            descripcion="Desc",
        )
        msg = MensajeTicket.objects.create(
            ticket=ticket,
            autor=self.admin,
            es_admin=True,
            contenido="Respuesta del soporte",
        )
        self.assertTrue(msg.es_admin)
        self.assertEqual(ticket.mensajes.count(), 1)


# ---------------------------------------------------------------------------
# Control de acceso a vistas
# ---------------------------------------------------------------------------

class AdminViewAccessTest(AdminPanelSetupMixin, TestCase):

    ADMIN_URLS = [
        "admin_dashboard",
        "crear_codigos",
        "ver_codigos",
        "gestionar_planes",
        "admin_usuarios",
        "historial_pagos",
        "tickets_soporte",
    ]

    def test_vistas_redirigen_sin_login(self):
        for name in self.ADMIN_URLS:
            with self.subTest(view=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn("/login/", response.url)

    def test_vistas_redirigen_usuario_normal(self):
        self.client.login(username="user_test", password="testpass123")
        for name in self.ADMIN_URLS:
            with self.subTest(view=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)

    def test_vistas_accesibles_para_staff(self):
        self.client.login(username="admin_test", password="testpass123")
        for name in self.ADMIN_URLS:
            with self.subTest(view=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_contactar_soporte_accesible_sin_login(self):
        response = self.client.get(reverse("contactar_soporte"))
        self.assertEqual(response.status_code, 200)

    def test_mis_tickets_requiere_login(self):
        response = self.client.get(reverse("mis_tickets"))
        self.assertEqual(response.status_code, 302)

    def test_mis_tickets_accesible_usuario_normal(self):
        self.client.login(username="user_test", password="testpass123")
        response = self.client.get(reverse("mis_tickets"))
        self.assertEqual(response.status_code, 200)
