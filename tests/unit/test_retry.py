"""PGD-15 AC-7: the retry helper with a fake clock, a fake sleeper and seeded jitter.

No test sleeps for real and none reads the real clock. Every scripted failure is a
``GmailApiError`` (what the gateway raises for an HTTP error) or a transport exception.
"""

from __future__ import annotations

import logging
import random
import ssl
import time
from collections.abc import Callable
from datetime import timedelta

import httplib2
import pytest

from gmail_pdf.domain.errors import GmailApiError, RetryExhaustedError, RunCancelledError
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.infra import retry
from gmail_pdf.infra.retry import call_with_retry
from tests.fakes.fake_time import FakeCancelToken, FakeClock, FakeSleeper

pytestmark = pytest.mark.req("NFR-006", "AC-7")

METHOD = "list_message_ids"


class Script:
    """An operation that raises the scripted failures in order, then returns ``"ok"``."""

    def __init__(self, *failures: BaseException) -> None:
        self.failures = list(failures)
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return "ok"


def always(*failure: BaseException) -> Callable[[], str]:
    """An operation that raises one of ``failure`` forever (cycled)."""
    calls = 0

    def operation() -> str:
        nonlocal calls
        calls += 1
        raise failure[(calls - 1) % len(failure)]

    return operation


def run(
    operation: Callable[[], str],
    *,
    jitter: Callable[[float, float], float] = lambda low, high: high,
    clock: FakeClock | None = None,
    cancel_during_sleep: int | None = None,
) -> tuple[str, FakeSleeper]:
    """Run ``operation`` through the helper; return its result and the sleeper."""
    sleeper = FakeSleeper(clock)
    token = FakeCancelToken(sleeper, cancel_during_sleep)
    result = call_with_retry(
        operation, method=METHOD, cancel=token, now=sleeper.clock.now, jitter=jitter
    )
    return result, sleeper


# ------------------------------------------------------------------ what is retried
RETRYABLE: list[tuple[str, BaseException]] = [
    ("http-429", GmailApiError(429)),
    ("http-500", GmailApiError(500)),
    ("http-502", GmailApiError(502)),
    ("http-503", GmailApiError(503)),
    ("http-504", GmailApiError(504)),
    ("403-rate-limit", GmailApiError(403, "rateLimitExceeded")),
    ("403-user-rate-limit", GmailApiError(403, "userRateLimitExceeded")),
    ("timeout", TimeoutError("scripted")),
    ("connection-reset", ConnectionResetError("scripted")),
    ("ssl", ssl.SSLError("scripted")),
    ("httplib2-dns", httplib2.ServerNotFoundError("scripted")),
]


@pytest.mark.parametrize("failure", [f for _, f in RETRYABLE], ids=[name for name, _ in RETRYABLE])
def test_retryable_failures_are_retried_until_the_call_succeeds(failure: BaseException) -> None:
    script = Script(failure, failure)

    result, sleeper = run(script)

    assert (result, script.calls, len(sleeper.delays)) == ("ok", 3, 2)


NOT_RETRYABLE: list[tuple[str, GmailApiError]] = [
    ("400", GmailApiError(400)),
    ("401", GmailApiError(401)),
    ("403-other-reason", GmailApiError(403, "insufficientPermissions")),
    ("403-no-reason", GmailApiError(403)),
    ("404", GmailApiError(404)),
    ("501", GmailApiError(501)),
]


@pytest.mark.parametrize(
    "failure", [f for _, f in NOT_RETRYABLE], ids=[name for name, _ in NOT_RETRYABLE]
)
def test_other_http_errors_are_raised_at_once_as_the_domain_error(failure: GmailApiError) -> None:
    script = Script(failure)

    with pytest.raises(GmailApiError) as exc_info:
        run(script)

    assert (exc_info.value is failure, script.calls) == (True, 1)


def test_an_exception_that_is_not_a_gmail_error_passes_through_unchanged() -> None:
    script = Script(ValueError("programming error"))

    with pytest.raises(ValueError, match="programming error"):
        run(script)

    assert script.calls == 1


def test_a_success_on_the_first_attempt_never_sleeps() -> None:
    result, sleeper = run(Script())

    assert (result, sleeper.delays) == ("ok", [])


# ------------------------------------------------------------------ attempts and delays
def test_there_are_six_attempts_and_five_sleeps_then_the_call_gives_up() -> None:
    calls: list[int] = []

    def operation() -> str:
        calls.append(1)
        raise GmailApiError(503)

    with pytest.raises(RetryExhaustedError) as exc_info:
        run(operation)

    assert len(calls) == 6
    assert exc_info.value.attempts == 6
    assert isinstance(exc_info.value.__cause__, GmailApiError)


def test_the_longest_possible_delays_double_from_one_second() -> None:
    operation = always(GmailApiError(503))
    sleeper = FakeSleeper()

    with pytest.raises(RetryExhaustedError):
        call_with_retry(
            operation,
            method=METHOD,
            cancel=FakeCancelToken(sleeper),
            now=sleeper.clock.now,
            jitter=lambda low, high: high,
        )

    assert sleeper.delays == [1.0, 2.0, 4.0, 8.0, 16.0]


def test_the_shortest_possible_delay_is_zero() -> None:
    _, sleeper = run(Script(*[GmailApiError(503)] * 5), jitter=lambda low, high: low)

    assert sleeper.delays == [0.0] * 5


def test_jitter_is_drawn_between_zero_and_the_cap_of_that_attempt() -> None:
    seen: list[tuple[float, float]] = []

    def recording_jitter(low: float, high: float) -> float:
        seen.append((low, high))
        return high / 2

    _, sleeper = run(Script(*[GmailApiError(503)] * 5), jitter=recording_jitter)

    assert seen == [(0.0, 1.0), (0.0, 2.0), (0.0, 4.0), (0.0, 8.0), (0.0, 16.0)]
    assert sleeper.delays == [0.5, 1.0, 2.0, 4.0, 8.0]


def test_seeded_jitter_gives_the_same_delays_every_time_and_stays_in_bounds() -> None:
    def delays(seed: int) -> list[float]:
        return run(Script(*[GmailApiError(429)] * 5), jitter=random.Random(seed).uniform)[1].delays

    first = delays(2026)

    assert first == delays(2026)
    assert all(0.0 <= delay <= cap for delay, cap in zip(first, [1, 2, 4, 8, 16], strict=True))
    assert first != delays(2027)


def test_the_backoff_cap_is_sixty_four_seconds() -> None:
    assert retry.backoff_delay(9, None, FakeClock().now, lambda low, high: high) == 64.0
    assert retry.backoff_delay(30, None, FakeClock().now, lambda low, high: high) == 64.0


# ------------------------------------------------------------------ Retry-After
def test_retry_after_in_seconds_replaces_the_jittered_delay() -> None:
    _, sleeper = run(Script(GmailApiError(429, retry_after="7")))

    assert sleeper.delays == [7.0]


def test_retry_after_as_an_http_date_is_measured_against_the_clock() -> None:
    clock = FakeClock()
    date = (clock.now() + timedelta(seconds=12)).strftime("%a, %d %b %Y %H:%M:%S GMT")

    _, sleeper = run(Script(GmailApiError(503, retry_after=date)), clock=clock)

    assert sleeper.delays == [12.0]


def test_retry_after_is_honoured_per_attempt_and_otherwise_jitter_is_used() -> None:
    script = Script(GmailApiError(429, retry_after="3"), GmailApiError(503))

    _, sleeper = run(script)

    assert sleeper.delays == [3.0, 2.0]


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        pytest.param("0", 0.0, id="zero"),
        pytest.param("64", 64.0, id="at-the-cap"),
        pytest.param("65", 64.0, id="over-the-cap"),
        pytest.param("9" * 5000, 64.0, id="absurdly-long-number"),
        pytest.param("Wed, 14 Jan 2026 12:00:00 GMT", 0.0, id="date-in-the-past"),
        pytest.param("Thu, 15 Jan 2026 12:30:00 GMT", 64.0, id="date-far-in-the-future"),
        pytest.param(" 5 ", 5.0, id="padded"),
    ],
)
def test_retry_after_is_clamped_to_zero_to_sixty_four_seconds(header: str, expected: float) -> None:
    delay = retry.backoff_delay(2, header, FakeClock().now, lambda low, high: high)

    assert delay == expected


@pytest.mark.parametrize(
    "header",
    [
        pytest.param("soon", id="words"),
        pytest.param("-5", id="negative"),
        pytest.param("1.5", id="fraction"),
        pytest.param("٥", id="arabic-indic-digit"),
        pytest.param("", id="empty"),
        pytest.param("Fri, 99 Foo 2026 99:99:99 GMT", id="garbage-date"),
    ],
)
def test_an_unusable_retry_after_falls_back_to_the_jittered_delay(header: str) -> None:
    delay = retry.backoff_delay(3, header, FakeClock().now, lambda low, high: high)

    assert delay == 2.0


def test_a_date_without_a_zone_is_read_as_utc() -> None:
    clock = FakeClock()
    naive = (clock.now() + timedelta(seconds=9)).strftime("%d %b %Y %H:%M:%S -0000")

    assert retry.parse_retry_after(naive, clock.now) == 9.0


# ------------------------------------------------------------------ cancel
def test_a_token_that_is_already_set_stops_before_the_first_call() -> None:
    script = Script()
    token = CancelToken()
    token.set()

    with pytest.raises(RunCancelledError):
        call_with_retry(script, method=METHOD, cancel=token)

    assert script.calls == 0


def test_cancel_during_a_backoff_stops_the_run_without_another_attempt() -> None:
    script = Script(*[GmailApiError(503)] * 5)

    with pytest.raises(RunCancelledError):
        run(script, cancel_during_sleep=2)

    assert script.calls == 2


def test_a_real_token_set_during_a_long_backoff_interrupts_it_at_once() -> None:
    token = CancelToken()

    def operation() -> str:
        token.set()  # the user pressed Cancel while this call was in flight
        raise GmailApiError(429, retry_after="60")

    started = time.monotonic()
    with pytest.raises(RunCancelledError):
        call_with_retry(operation, method=METHOD, cancel=token)

    assert time.monotonic() - started < 10


# ------------------------------------------------------------------ logging
def test_each_retry_logs_the_method_the_attempt_and_the_delay_only(
    caplog: pytest.LogCaptureFixture,
) -> None:
    failure = GmailApiError(429, "rateLimitExceeded", retry_after="4")
    with caplog.at_level(logging.DEBUG, logger="gmail_pdf.infra.retry"):
        run(Script(failure, GmailApiError(503)))

    assert [(r.levelno, r.getMessage()) for r in caplog.records] == [
        (logging.WARNING, "Retrying list_message_ids: attempt 2 of 6 after 4.0 s"),
        (logging.WARNING, "Retrying list_message_ids: attempt 3 of 6 after 2.0 s"),
    ]


def test_the_exhaustion_error_text_is_a_fixed_sentence() -> None:
    with pytest.raises(RetryExhaustedError) as exc_info:
        run(always(TimeoutError("secret detail")))

    assert str(exc_info.value) == "Gmail could not be reached after 6 attempts."


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        pytest.param(GmailApiError(503), True, id="gmail-503"),
        pytest.param(GmailApiError(404), False, id="gmail-404"),
        pytest.param(OSError("disk"), False, id="plain-os-error"),
        pytest.param(RuntimeError("x"), False, id="runtime-error"),
        pytest.param(TimeoutError(), True, id="timeout"),
    ],
)
def test_is_retryable_classifies_by_type(error: BaseException, expected: bool) -> None:
    assert retry.is_retryable(error) is expected
