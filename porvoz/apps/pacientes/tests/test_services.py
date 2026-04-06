"""
Tests para PacienteService.
Ejecutar: python manage.py test apps.pacientes
"""

from django.test import TestCase
from django.contrib.auth.models import User

from apps.pacientes.services import PacienteService
from apps.pacientes.models import Paciente


class PacienteServiceCrearTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )

    def test_crear_paciente_exitoso(self):
        paciente = PacienteService.crear_paciente(
            usuario=self.user,
            nombre="Juan Pérez",
            telefono="+573001234567",
        )
        self.assertEqual(paciente.nombre, "Juan Pérez")
        self.assertEqual(paciente.usuario, self.user)
        self.assertTrue(paciente.activo)

    def test_crear_paciente_usuario_mismo(self):
        paciente = PacienteService.crear_paciente(
            usuario=self.user,
            nombre="Yo mismo",
            telefono="+573009999999",
            es_usuario_mismo=True,
        )
        self.assertTrue(paciente.es_usuario_mismo)

    def test_crear_enfermedad(self):
        paciente = PacienteService.crear_paciente(
            usuario=self.user,
            nombre="María López",
            telefono="+573007777777",
        )
        enfermedad = PacienteService.crear_enfermedad(
            paciente=paciente,
            nombre="Diabetes tipo 2",
            descripcion="Controlada con medicamentos",
        )
        self.assertEqual(enfermedad.nombre, "Diabetes tipo 2")
        self.assertEqual(enfermedad.paciente, paciente)
        self.assertTrue(enfermedad.activa)


class PacienteServiceValidacionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser2",
            email="test2@test.com",
            password="testpass123",
        )
        PacienteService.crear_paciente(
            usuario=self.user,
            nombre="Paciente Existente",
            telefono="+573001111111",
        )

    def test_verificar_telefono_existente_retorna_true(self):
        existe = PacienteService.verificar_telefono_existente(
            usuario=self.user,
            telefono="+573001111111",
        )
        self.assertTrue(existe)

    def test_verificar_telefono_nuevo_retorna_false(self):
        existe = PacienteService.verificar_telefono_existente(
            usuario=self.user,
            telefono="+573009876543",
        )
        self.assertFalse(existe)

    def test_verificar_telefono_excluir_id(self):
        paciente = Paciente.objects.get(telefono="+573001111111", usuario=self.user)
        existe = PacienteService.verificar_telefono_existente(
            usuario=self.user,
            telefono="+573001111111",
            paciente_excluir_id=paciente.id,
        )
        self.assertFalse(existe)


class PacienteServiceBusquedaTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser3",
            email="test3@test.com",
            password="testpass123",
        )
        self.p1 = PacienteService.crear_paciente(
            usuario=self.user, nombre="Carlos García", telefono="+573001234501"
        )
        self.p2 = PacienteService.crear_paciente(
            usuario=self.user, nombre="María López", telefono="+573001234502"
        )

    def test_buscar_por_nombre(self):
        pacientes = list(Paciente.objects.filter(usuario=self.user))
        resultado = PacienteService.buscar_pacientes(pacientes, "carlos")
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].nombre, "Carlos García")

    def test_buscar_sin_filtro_retorna_todos(self):
        pacientes = list(Paciente.objects.filter(usuario=self.user))
        resultado = PacienteService.buscar_pacientes(pacientes, "")
        self.assertEqual(len(resultado), 2)

    def test_buscar_sin_tildes(self):
        pacientes = list(Paciente.objects.filter(usuario=self.user))
        resultado = PacienteService.buscar_pacientes(pacientes, "garcia")
        self.assertEqual(len(resultado), 1)


class PacienteServiceTelefonoTest(TestCase):
    def test_es_telefono_usuario_mismo_coincidencia(self):
        resultado = PacienteService.es_telefono_usuario_mismo(
            "+573001234567", "+573001234567"
        )
        self.assertTrue(resultado)

    def test_es_telefono_usuario_mismo_sin_prefijo(self):
        resultado = PacienteService.es_telefono_usuario_mismo(
            "+573001234567", "3001234567"
        )
        self.assertTrue(resultado)

    def test_es_telefono_usuario_mismo_diferente(self):
        resultado = PacienteService.es_telefono_usuario_mismo(
            "+573001234567", "+573009999999"
        )
        self.assertFalse(resultado)

    def test_es_telefono_usuario_mismo_vacio(self):
        resultado = PacienteService.es_telefono_usuario_mismo("", "+573001234567")
        self.assertFalse(resultado)
