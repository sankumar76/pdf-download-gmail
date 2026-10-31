"""Retry with backoff for Gmail calls (NFR-006, architecture 6.4, ADR-006).

This is the only retry in the program: the Google client library's own retry is switched off
(``execute(num_retries=0)``) because it ignores ``Retry-After``.

* Retryable: HTTP 429, 500, 502, 503, 504; HTTP 403 with reason ``rateLimitExceeded`` or
  ``userRateLimitExceeded``; transport errors (``TimeoutError``, ``ConnectionError``,
  ``ssl.SSLError``, ``httplib2.ServerNotFoundError``).
* Not retryable: every other HTTP status (``GmailApiError`` is raised at once) and any other
  exception, which passes through unchanged.
* Six attempts in total. The delay before attempt *n* (n >= 2) is ``Retry-After`` when the
  server sent a usable one, otherwise ``uniform(0, min(64, 2 ** (n - 2)))`` seconds; always
  clamped to 0..64 s.
* A backoff sleeps with ``cancel.wait(delay)``, so cancelling interrupts it at once, and the
  token is checked before every attempt.
* Each retry is logged with the method name, the attempt number and the delay, and nothing else:
  never the URL, the query or the headers.

The helper sees domain errors only: ``infra.gmail_gateway`` turns the Google library's
``HttpError`` into ``GmailApiError`` first, so this module imports nothing from Google.
"""

from __future__ import annotations

import logging
import random
import ssl
from collections.abc import Callable
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import TypeVar

from gmail_pdf.domain.errors import GmailApiError, RetryExhaustedError, RunCancelledError
from gmail_pdf.domain.events import CancelToken

logger = logging.getLogger(__name__)

T = TypeVar("T")

MAX_ATTEMPTS = 6
MAX_DELAY_S = 64.0
BACKOFF_BASE_S = 1.0
RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})
RATE_LIMIT_REASONS = frozenset({"rateLimitExceeded", "userRateLimitExceeded"})
HTTP_FORBIDDEN = 403

_TRANSPORT_ERRORS = (TimeoutError, ConnectionError, ssl.SSLError)
# Recognised by qualified class name so httplib2 (a transitive dependency of the Google client)
# is not imported here, as ``redaction`` does for third-party exception types.
_TRANSPORT_ERROR_NAMES = frozenset(
    {"httplib2.error.ServerNotFoundError", "httplib2.ServerNotFoundError"}
)
# Jitter needs no secrecy; the system source keeps the standard library's seeded generator (and
# the security linters' warning about it) out of production code. Tests pass a seeded callable.
SYSTEM_JITTER: Callable[[float, float], float] = random.SystemRandom().uniform


def utc_now() -> datetime:
    """The current time, timezone-aware (UTC)."""
    return datetime.now(timezone.utc)


def is_retryable(error: BaseException) -> bool:
    """Whether a failed Gmail call is worth repeating (architecture 6.4)."""
    if isinstance(error, GmailApiError):
        return error.status in RETRYABLE_STATUSES or (
            error.status == HTTP_FORBIDDEN and error.reason in RATE_LIMIT_REASONS
        )
    if isinstance(error, _TRANSPORT_ERRORS):
        return True
    names = {f"{cls.__module__}.{cls.__qualname__}" for cls in type(error).__mro__}
    return bool(names & _TRANSPORT_ERROR_NAMES)


def parse_retry_after(value: str | None, now: Callable[[], datetime]) -> float | None:
    """Seconds to wait according to a ``Retry-After`` header value, or ``None`` if unusable.

    Accepts whole seconds or an HTTP date (RFC 9110). A date in the past gives 0.
    """
    if value is None:
        return None
    text = value.strip()
    if text.isascii() and text.isdecimal():
        return float(text)  # float, not int: a very long digit string must not raise
    try:
        moment = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return max((moment - now()).total_seconds(), 0.0)


def backoff_delay(
    attempt: int,
    retry_after: str | None,
    now: Callable[[], datetime],
    jitter: Callable[[float, float], float],
) -> float:
    """Seconds to sleep before ``attempt`` (2 or more), clamped to 0..64."""
    delay = parse_retry_after(retry_after, now)
    if delay is None:
        delay = jitter(0.0, min(MAX_DELAY_S, BACKOFF_BASE_S * 2 ** (attempt - 2)))
    return min(max(delay, 0.0), MAX_DELAY_S)


def call_with_retry(
    operation: Callable[[], T],
    *,
    method: str,
    cancel: CancelToken,
    now: Callable[[], datetime] = utc_now,
    jitter: Callable[[float, float], float] = SYSTEM_JITTER,
) -> T:
    """Call ``operation`` until it succeeds, fails for good, or the attempts run out.

    Args:
        operation: One attempt; it is called again for every retry.
        method: Name of the Gmail method, for the log line only.
        cancel: Checked before every attempt and waited on during a backoff.
        now: Clock for HTTP-date ``Retry-After`` values (a fake in tests).
        jitter: ``uniform(low, high)`` (seeded in tests).

    Raises:
        RunCancelledError: ``cancel`` was set before an attempt or during a backoff.
        RetryExhaustedError: every one of the attempts failed with a retryable error.
        GmailApiError: a non-retryable HTTP error, raised at once.
    """
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        if cancel.is_set():
            raise RunCancelledError
        try:
            return operation()
        except Exception as error:
            if not is_retryable(error):
                raise
            last_error = error
        if attempt == MAX_ATTEMPTS:
            break
        retry_after = last_error.retry_after if isinstance(last_error, GmailApiError) else None
        delay = backoff_delay(attempt + 1, retry_after, now, jitter)
        logger.warning(
            "Retrying %s: attempt %d of %d after %.1f s", method, attempt + 1, MAX_ATTEMPTS, delay
        )
        if cancel.wait(delay):
            raise RunCancelledError
    raise RetryExhaustedError(MAX_ATTEMPTS) from last_error
