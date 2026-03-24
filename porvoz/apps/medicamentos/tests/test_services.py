"""
Tests para MedicamentoService.
Ejecutar: python manage.py test apps.medicamentos
"""

from django.test import TestCase
from django.contrib.auth.models import User

from apps.pacientes.models import Paciente
from apps.medicamentos.models import Medicamento, HorarioMedicamento
from apps.medicamentos.services import MedicamentoService


class MedicamentoServiceCrearTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre="Paciente Test",
            telefono="+573001234567",
        )

    def test_crear_medicamento_horario_especifico(self):
        medicamento = MedicamentoService.crear_medicamento(
            paciente=self.paciente,
            nombre="Aspirina",
            dosis="100mg",
            frecuencia_tipo=Medicamento.FRECUENCIA_HORARIO,
            horarios=["08:00", "20:00"],
        )
        self.assertEqual(medicamento.nombre, "Aspirina")
        self.assertEqual(medicamento.paciente, self.paciente)
        self.assertTrue(medicamento.activo)

    def test_crear_medicamento_crea_horarios(self):
        medicamento = MedicamentoService.crear_medicamento(
            paciente=self.paciente,
            nombre="Metformina",
            dosis="500mg",
            frecuencia_tipo=Medicamento.FRECUENCIA_HORARIO,
            horarios=["07:00", "13:00", "21:00"],
        )
        horarios = HorarioMedicamento.objects.filter(medicamento=medicamento)
        self.assertEqual(horarios.count(), 3)

    def test_crear_medicamento_cada_x_horas(self):
        medicamento = MedicamentoService.crear_medicamento(
            paciente=self.paciente,
            nombre="Antibiótico",
            dosis="250mg",
            frecuencia_tipo=Medicamento.FRECUENCIA_CADA_X_HORAS,
            cada_x_horas=8,
            hora_inicio="08:00",
        )
        self.assertEqual(medicamento.frecuencia_tipo, Medicamento.FRECUENCIA_CADA_X_HORAS)
        self.assertEqual(medicamento.cada_x_horas, 8)

    def test_crear_medicamento_activo_por_defecto(self):
        medicamento = MedicamentoService.crear_medicamento(
            paciente=self.paciente,
            nombre="Vitamina C",
            dosis="500mg",
            horarios=["09:00"],
        )
        self.assertTrue(medicamento.activo)


class MedicamentoServiceToggleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser2",
            email="test2@test.com",
            password="testpass123",
        )
        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre="Paciente Test",
            telefono="+573009999999",
        )
        self.medicamento = MedicamentoService.crear_medicamento(
            paciente=self.paciente,
            nombre="Enalapril",
            dosis="10mg",
            horarios=["08:00"],
        )

    def test_toggle_desactiva_medicamento_activo(self):
        self.assertTrue(self.medicamento.activo)
        nuevo_estado = MedicamentoService.toggle_medicamento(self.medicamento)
        self.assertFalse(nuevo_estado)
        self.medicamento.refresh_from_db()
        self.assertFalse(self.medicamento.activo)

    def test_toggle_activa_medicamento_inactivo(self):
        self.medicamento.activo = False
        self.medicamento.save()
        nuevo_estado = MedicamentoService.toggle_medicamento(self.medicamento)
        self.assertTrue(nuevo_estado)


class MedicamentoServiceActualizarTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser3",
            email="test3@test.com",
            password="testpass123",
        )
        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre="Paciente Test",
            telefono="+573008888888",
        )
        self.medicamento = MedicamentoService.crear_medicamento(
            paciente=self.paciente,
            nombre="Medicamento Original",
            dosis="100mg",
            horarios=["08:00"],
        )

    def test_actualizar_nombre_y_dosis(self):
        MedicamentoService.actualizar_medicamento(
            medicamento=self.medicamento,
            nombre="Medicamento Actualizado",
            dosis="200mg",
            horarios=["09:00"],
        )
        self.medicamento.refresh_from_db()
        self.assertEqual(self.medicamento.nombre, "Medicamento Actualizado")
        self.assertEqual(self.medicamento.dosis, "200mg")

    def test_actualizar_reemplaza_horarios(self):
        MedicamentoService.actualizar_medicamento(
            medicamento=self.medicamento,
            nombre="Medicamento Original",
            dosis="100mg",
            horarios=["10:00", "22:00"],
        )
        horarios = HorarioMedicamento.objects.filter(medicamento=self.medicamento)
        self.assertEqual(horarios.count(), 2)
