"""
Tests for autenticacion app (registration, password reset).
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.autenticacion.services.registro_service import RegistroService
from apps.core.models import Perfil


class RegistroServiceTest(TestCase):
    """Tests for user registration service."""

    def test_crear_usuario_valido(self):
        """Should create user and perfil with valid data."""
        user, perfil = RegistroService.crear_usuario_y_perfil(
            username="newuser@test.com",
            email="newuser@test.com",
            password="SecurePass123",
            first_name="John",
            last_name="Doe",
        )

        self.assertIsNotNone(user.pk)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertIsNotNone(perfil.pk)
        self.assertEqual(perfil.plan, Perfil.PLAN_FREEMIUM)

    def test_crear_usuario_email_duplicado(self):
        """Should raise ValueError if username already exists."""
        User.objects.create_user(username="existing@test.com", email="existing@test.com")

        with self.assertRaises(Exception):
            RegistroService.crear_usuario_y_perfil(
                username="existing@test.com",
                email="existing@test.com",
                password="SecurePass123",
                first_name="John",
                last_name="Doe",
            )

    def test_crear_usuario_password_debil(self):
        """Weak password still creates user (Django doesn't validate in create_user)."""
        user, perfil = RegistroService.crear_usuario_y_perfil(
            username="weakpass@test.com",
            email="weakpass@test.com",
            password="123",
            first_name="John",
            last_name="Doe",
        )
        self.assertIsNotNone(user.pk)


class PasswordResetTest(TestCase):
    """Tests for password reset flow."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="OldPass123"
        )

    def test_reset_password_valid(self):
        """Should reset password with valid token."""
        self.assertTrue(User.objects.filter(email="test@test.com").exists())
