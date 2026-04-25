"""
Tests for shared utilities (TelefonoService, decorators, exceptions).
"""

from django.core.cache import cache
from django.test import TestCase, RequestFactory
from apps.shared.services.telefono_service import TelefonoService
from apps.shared.decorators import rate_limit_by_key, deduplicate_webhook
from django.http import HttpResponse


class TelefonoServiceTest(TestCase):
    """Tests for phone number parsing and validation."""

    def test_es_numero_valido_colombia(self):
        """Should validate Colombian phone numbers."""
        self.assertTrue(TelefonoService.es_numero_valido("3001234567"))
        self.assertTrue(TelefonoService.es_numero_valido("+573001234567"))

    def test_es_numero_invalido(self):
        """Should reject invalid phone numbers."""
        self.assertFalse(TelefonoService.es_numero_valido("123"))
        self.assertFalse(TelefonoService.es_numero_valido("abcdefghij"))

    def test_normalizar_telefono(self):
        """Should normalize phone numbers to E.164."""
        result = TelefonoService.normalizar_telefono("3001234567")
        self.assertEqual(result, "+573001234567")

        result = TelefonoService.normalizar_telefono("+573001234567")
        self.assertEqual(result, "+573001234567")

    def test_obtener_codigo_pais(self):
        """Should extract country code from phone."""
        code = TelefonoService.obtener_codigo_pais("+573001234567")
        self.assertEqual(code, "+57")

    def test_parsear_telefono_sin_prefijo(self):
        """Should default to +57 for numbers without country code."""
        parsed = TelefonoService.parsear_telefono("3001234567")
        self.assertEqual(parsed.pais, "+57")
        self.assertEqual(parsed.numero, "3001234567")

    def test_sanitizar_numero(self):
        """Should strip spaces and dashes from number."""
        result = TelefonoService.sanitizar_numero("300-123 4567")
        self.assertEqual(result, "3001234567")


class RateLimitDecoratorTest(TestCase):
    """Tests for rate limiting decorator."""

    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def test_rate_limit_allows_requests(self):
        """Should allow requests under the limit."""
        call_count = [0]

        @rate_limit_by_key(key_func=lambda r: "rl_allow_test", rate="3/s")
        def view(request):
            call_count[0] += 1
            return HttpResponse("OK")

        for _ in range(2):
            request = self.factory.post("/")
            response = view(request)
            self.assertEqual(response.status_code, 200)

        self.assertEqual(call_count[0], 2)

    def test_rate_limit_blocks_exceeded(self):
        """Should return 429 when limit exceeded."""
        @rate_limit_by_key(key_func=lambda r: "rl_block_test", rate="1/s")
        def view(request):
            return HttpResponse("OK")

        request = self.factory.post("/")
        response = view(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post("/")
        response = view(request)
        self.assertEqual(response.status_code, 429)


class DeduplicateWebhookTest(TestCase):
    """Tests for webhook deduplication."""

    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def test_deduplicate_allows_first_webhook(self):
        """Should allow first webhook through."""
        call_count = [0]

        @deduplicate_webhook(key_func=lambda r: r.POST.get("CallSid"), ttl=60)
        def view(request):
            call_count[0] += 1
            return HttpResponse("OK", status=200)

        request = self.factory.post("/", {"CallSid": "call_allow_123"})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(call_count[0], 1)

    def test_deduplicate_blocks_duplicate(self):
        """Should return 200 but not process duplicate webhook."""
        call_count = [0]

        @deduplicate_webhook(key_func=lambda r: r.POST.get("CallSid"), ttl=60)
        def view(request):
            call_count[0] += 1
            return HttpResponse("OK", status=200)

        request = self.factory.post("/", {"CallSid": "call_dup_456"})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(call_count[0], 1)

        request = self.factory.post("/", {"CallSid": "call_dup_456"})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(call_count[0], 1)
