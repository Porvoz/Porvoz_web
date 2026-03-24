"""
Tests para servicios de llamadas.
Ejecutar: python manage.py test apps.llamadas

Nota: Tests implementados en Sprint 2 cuando se agreguen modelos y servicios.
"""

from django.test import TestCase


class LlamadaServiceTest(TestCase):
    """Tests para LlamadaService."""

    def test_crear_llamada_programada(self):
        """Test: crear una llamada programada desde un medicamento."""
        # TODO: Implementar en Sprint 2
        pass

    def test_ejecutar_llamada_automatica(self):
        """Test: disparar una llamada automática."""
        # TODO: Implementar en Sprint 2
        pass

    def test_registrar_respuesta_confirmada(self):
        """Test: registrar respuesta confirmada."""
        # TODO: Implementar en Sprint 2
        pass

    def test_registrar_respuesta_negada_crea_alerta(self):
        """Test: respuesta negada crea una Notificación de ALERTA."""
        # TODO: Implementar en Sprint 2
        pass
