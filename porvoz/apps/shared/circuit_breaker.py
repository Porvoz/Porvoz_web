"""
Redis-based circuit breaker for external service calls (Twilio, Gemini).

States:
  CLOSED   → normal operation, requests pass through
  OPEN     → service considered down, requests fail fast
  HALF_OPEN → recovery window: allows one probe request
"""

import logging
import time

from django.core.cache import cache

logger = logging.getLogger(__name__)

_CLOSED = "closed"
_OPEN = "open"
_HALF_OPEN = "half_open"

_TTL = 300  # key TTL in cache (5 min — longer than any recovery timeout)


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

    def _k(self, suffix: str) -> str:
        return f"cb:{self.name}:{suffix}"

    def state(self) -> str:
        raw = cache.get(self._k("state"), _CLOSED)
        if raw == _OPEN:
            opened_at = cache.get(self._k("opened_at"), 0)
            if time.time() - opened_at >= self.recovery_timeout:
                return _HALF_OPEN
        return raw

    def is_open(self) -> bool:
        return self.state() == _OPEN

    def call(self, func, *args, fallback=None, **kwargs):
        """
        Execute func inside the circuit breaker.
        If OPEN, call fallback (if provided) or raise RuntimeError.
        """
        current = self.state()

        if current == _OPEN:
            logger.warning("[CB:%s] OPEN — fast fail", self.name)
            if fallback is not None:
                return fallback() if callable(fallback) else fallback
            raise RuntimeError(f"Circuit breaker '{self.name}' is OPEN")

        try:
            result = func(*args, **kwargs)
        except Exception:
            self._record_failure()
            raise
        else:
            self._record_success(current)
            return result

    def _record_success(self, previous_state: str):
        if previous_state == _HALF_OPEN:
            successes = cache.get(self._k("successes"), 0) + 1
            cache.set(self._k("successes"), successes, _TTL)
            if successes >= self.success_threshold:
                self._close()
        else:
            cache.set(self._k("failures"), 0, _TTL)

    def _record_failure(self):
        failures = cache.get(self._k("failures"), 0) + 1
        cache.set(self._k("failures"), failures, _TTL)
        if failures >= self.failure_threshold:
            self._open()

    def _open(self):
        cache.set(self._k("state"), _OPEN, _TTL)
        cache.set(self._k("opened_at"), time.time(), _TTL)
        cache.set(self._k("successes"), 0, _TTL)
        logger.error("[CB:%s] → OPEN (failures reached threshold)", self.name)

    def _close(self):
        cache.set(self._k("state"), _CLOSED, _TTL)
        cache.set(self._k("failures"), 0, _TTL)
        cache.set(self._k("successes"), 0, _TTL)
        logger.info("[CB:%s] → CLOSED (recovered)", self.name)


# Singleton breakers — shared across all requests in the same process.
twilio_breaker = CircuitBreaker(
    name="twilio",
    failure_threshold=5,
    recovery_timeout=120,
    success_threshold=2,
)

gemini_breaker = CircuitBreaker(
    name="gemini",
    failure_threshold=3,
    recovery_timeout=60,
    success_threshold=1,
)
