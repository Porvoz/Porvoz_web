"""
Tests for usuarios app (profile, password changes, plan limits).
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from apps.core.models import Perfil
from apps.pacientes.models import Paciente
from apps.usuarios.services.perfil_service import PerfilService
from apps.usuarios.services.planes_service import PlanService


class PerfilServiceTest(TestCase):
    """Tests for profile management service."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="OldPass123"
        )
        self.perfil = Perfil.objects.create(user=self.user)

    def test_actualizar_perfil_valido(self):
        """Should update profile fields correctly."""
        success, error = PerfilService.actualizar_perfil(
            self.perfil,
            first_name="Juan",
            last_name="García",
            city="Medellín",
        )
        self.assertTrue(success)
        self.assertIsNone(error)
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.first_name, "Juan")
        self.assertEqual(self.perfil.city, "Medellín")

    def test_dias_restantes_plan_con_fecha(self):
        """Should return days remaining when plan_expiration is set."""
        self.perfil.plan_expiration = date.today() + timedelta(days=30)
        self.perfil.save()
        dias = PerfilService.get_dias_restantes_plan(self.perfil)
        self.assertGreaterEqual(dias, 29)
        self.assertLessEqual(dias, 30)

    def test_dias_restantes_plan_sin_fecha(self):
        """Should return 365 when no expiration date is set."""
        self.perfil.plan_expiration = None
        self.perfil.save()
        dias = PerfilService.get_dias_restantes_plan(self.perfil)
        self.assertEqual(dias, 365)

    def test_cambiar_plan_valido(self):
        """Should update plan to a valid key."""
        success, error = PerfilService.cambiar_plan(self.perfil, Perfil.PLAN_GROWTH)
        self.assertTrue(success)
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.plan, Perfil.PLAN_GROWTH)

    def test_cambiar_plan_invalido(self):
        """Should reject unknown plan key."""
        success, error = PerfilService.cambiar_plan(self.perfil, "plan_inexistente")
        self.assertFalse(success)
        self.assertIsNotNone(error)


class PlanServiceTest(TestCase):
    """Tests for plan limits enforcement."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="TestPass123"
        )
        self.perfil = Perfil.objects.create(user=self.user, plan=Perfil.PLAN_FREEMIUM)

    def test_paciente_limit_freemium(self):
        """Freemium plan should only allow 1 patient."""
        Paciente.objects.create(
            usuario=self.user,
            nombre="Paciente 1",
            telefono="3001234567"
        )
        puede, msg = PlanService.puede_agregar_paciente(self.user)
        self.assertFalse(puede)

    def test_paciente_limit_growth(self):
        """Growth plan should allow up to 3 patients."""
        self.perfil.plan = Perfil.PLAN_GROWTH
        self.perfil.save()

        for i in range(3):
            Paciente.objects.create(
                usuario=self.user,
                nombre=f"Paciente {i + 1}",
                telefono=f"+5730012345{i:02d}"
            )

        puede, msg = PlanService.puede_agregar_paciente(self.user)
        self.assertFalse(puede)

    def test_paciente_bajo_limite_growth(self):
        """Básico (growth) allows 1 patient — under limit when 0 exist."""
        self.perfil.plan = Perfil.PLAN_GROWTH
        self.perfil.save()

        # Sin pacientes aún → puede agregar el primero (límite = 1)
        puede, msg = PlanService.puede_agregar_paciente(self.user)
        self.assertTrue(puede)
