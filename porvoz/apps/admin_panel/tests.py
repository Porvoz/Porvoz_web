"""
Tests for admin panel views, models, and functionality.
"""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.admin_panel.models import CodigoAcceso, PagoHistorico, TicketSoporte
from apps.core.models import Perfil


class AdminPanelSetupTest(TestCase):
    """Test admin panel basic setup and access"""

    def setUp(self):
        """Create test data"""
        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="testpass123",
            is_staff=True,
            is_superuser=True,
        )
        Perfil.objects.create(
            user=self.admin_user,
            plan="empresa",
            plan_estado=Perfil.ESTADO_ACTIVO,
        )

        self.regular_user = User.objects.create_user(
            username="user_test",
            password="testpass123",
        )
        Perfil.objects.create(
            user=self.regular_user,
            plan="basico",
            plan_estado=Perfil.ESTADO_ACTIVO,
        )

        self.client = Client()

    def test_admin_dashboard_requires_login(self):
        """Test that admin dashboard requires login"""
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn("/login/", response.url)

    def test_admin_dashboard_requires_staff(self):
        """Test that admin dashboard requires staff privileges"""
        self.client.login(username="user_test", password="testpass123")
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirect or forbidden

    def test_admin_dashboard_accessible_to_staff(self):
        """Test that staff can access admin dashboard"""
        self.client.login(username="admin_test", password="testpass123")
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_panel/dashboard.html")

    def test_crear_codigos_requires_staff(self):
        """Test that crear_codigos requires staff privileges"""
        self.client.login(username="user_test", password="testpass123")
        response = self.client.get(reverse("crear_codigos"))
        self.assertEqual(response.status_code, 302)

    def test_ver_codigos_requires_staff(self):
        """Test that ver_codigos requires staff privileges"""
        self.client.login(username="user_test", password="testpass123")
        response = self.client.get(reverse("ver_codigos"))
        self.assertEqual(response.status_code, 302)


class CodigoAccesoTest(TestCase):
    """Test CodigoAcceso model"""

    def test_generar_codigo(self):
        """Test code generation"""
        codigo = CodigoAcceso.generar_codigo()
        self.assertIsNotNone(codigo)
        self.assertTrue(codigo.startswith("PROMO-"))
        self.assertEqual(len(codigo), 16)  # PROMO-XXXXXX-XXX

    def test_codigo_uniqueness(self):
        """Test that generated codes are unique"""
        admin = User.objects.create_user(username="admin", password="test", is_staff=True)
        codigo1 = CodigoAcceso.objects.create(
            codigo=CodigoAcceso.generar_codigo(),
            plan="basico",
            duracion_meses=1,
            creado_por=admin,
        )
        codigo2 = CodigoAcceso.objects.create(
            codigo=CodigoAcceso.generar_codigo(),
            plan="basico",
            duracion_meses=1,
            creado_por=admin,
        )
        self.assertNotEqual(codigo1.codigo, codigo2.codigo)

    def test_codigo_estados(self):
        """Test code state transitions"""
        admin = User.objects.create_user(username="admin", password="test", is_staff=True)
        codigo = CodigoAcceso.objects.create(
            codigo=CodigoAcceso.generar_codigo(),
            plan="basico",
            duracion_meses=1,
            creado_por=admin,
        )
        self.assertEqual(codigo.estado, CodigoAcceso.ESTADO_DISPONIBLE)


class PagoHistoricoTest(TestCase):
    """Test PagoHistorico model"""

    def test_crear_pago(self):
        """Test creating a payment record"""
        user = User.objects.create_user(username="user", password="test")
        pago = PagoHistorico.objects.create(
            usuario=user,
            plan="basico",
            duracion_meses=1,
            tipo_pago="codigo",
            fecha_hasta="2025-06-07",
        )
        self.assertIsNotNone(pago)
        self.assertEqual(pago.usuario, user)


class TicketSoporteTest(TestCase):
    """Test TicketSoporte model"""

    def test_crear_ticket(self):
        """Test creating a support ticket"""
        user = User.objects.create_user(username="user", password="test")
        ticket = TicketSoporte.objects.create(
            usuario=user,
            titulo="Test Ticket",
            descripcion="Test description",
            prioridad=TicketSoporte.PRIORIDAD_MEDIA,
        )
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.estado, TicketSoporte.ESTADO_ABIERTO)
