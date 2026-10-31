"""PGD-13 AC-5 and AC-8: the excepthook installers, the unexpected-failure and cancel lines.

Over 400 lines on purpose (Coding Standards, files): every test of the "nothing escapes"
guarantee for the hooks and the log filter (QUA-27, QUA-31, QUA-32) sits next to the one set of
breakers it uses; the split into its own module is planned for STORY-01.04 (TD-B).
"""

from __future__ import annotations

import io
import logging
import sys
import threading
import traceback
import types
from collections.abc import Callable, Iterator
from typing import NoReturn

import pytest

from gmail_pdf import redaction
from gmail_pdf.domain import messages
from gmail_pdf.redaction import (
    install_excepthooks,
    report_cancelled,
    report_unexpected_failure,
)
from tests.support import sentinels

pytestmark = pytest.mark.req("FR-005", "NFR-012")

FAILURE = messages.UNEXPECTED_FAILURE_LINE + "\n"
CANCELLED = messages.RUN_CANCELLED_LINE + "\n"


@pytest.fixture(autouse=True)
def _registered_secrets() -> None:
    for value in sentinels.REGISTERED:
        redaction.register_secret(value)


def secret_error() -> RuntimeError:
    """A raised error whose message, args and cause chain all carry sentinels."""
    try:
        try:
            raise ValueError(f"inner {sentinels.ACCESS_TOKEN}")
        except ValueError as inner:
            raise RuntimeError(
                f"{sentinels.CLIENT_SECRET} {sentinels.UNREGISTERED_GOCSPX}",
                sentinels.REFRESH_TOKEN,
            ) from inner
    except RuntimeError as outer:
        return outer


def call_main_hook(exc: BaseException) -> None:
    assert sys.excepthook is not sys.__excepthook__
    sys.excepthook(type(exc), exc, exc.__traceback__)


def run_in_worker(target: Callable[[], None]) -> None:
    worker = threading.Thread(target=target, name="worker-under-test")
    worker.start()
    worker.join(timeout=10)
    assert not worker.is_alive()


# ----------------------------------------------------------------------------------- install


HOOKS = [
    pytest.param(sys, "excepthook", id="sys.excepthook"),
    pytest.param(threading, "excepthook", id="threading.excepthook"),
    pytest.param(sys, "unraisablehook", id="sys.unraisablehook"),
]


@pytest.mark.parametrize(("owner", "name"), HOOKS)
@pytest.mark.req("AC-5")
def test_install_replaces_the_hook(owner: object, name: str) -> None:
    before = getattr(owner, name)

    install_excepthooks()

    assert getattr(owner, name) is not before


@pytest.mark.parametrize(("owner", "name"), HOOKS)
@pytest.mark.req("AC-5")
def test_restore_puts_the_previous_hook_back(owner: object, name: str) -> None:
    before = getattr(owner, name)
    restore = install_excepthooks()

    restore()

    assert getattr(owner, name) is before


def unraisable_args(exc: BaseException) -> types.SimpleNamespace:
    """Stands in for ``sys.UnraisableHookArgs`` (the hook only reads these fields)."""
    return types.SimpleNamespace(
        exc_type=type(exc),
        exc_value=exc,
        exc_traceback=exc.__traceback__,
        err_msg="Exception ignored in",
        object=None,
    )


@pytest.fixture
def ignored_exception() -> RuntimeError:
    return RuntimeError(f"{sentinels.CLIENT_SECRET} {sentinels.ACCESS_TOKEN}")


@pytest.mark.req("AC-5")
def test_an_ignored_exception_prints_nothing_to_stderr(
    capsys: pytest.CaptureFixture[str], ignored_exception: RuntimeError
) -> None:
    install_excepthooks()

    sys.unraisablehook(unraisable_args(ignored_exception))

    assert capsys.readouterr().err == ""


def hand_to_unraisable_hook(caplog: pytest.LogCaptureFixture, exc: RuntimeError) -> None:
    """Install the hooks, then hand ``exc`` to ``sys.unraisablehook`` with DEBUG captured."""
    install_excepthooks()
    caplog.set_level(logging.DEBUG, logger=redaction.logger.name)
    sys.unraisablehook(unraisable_args(exc))


@pytest.mark.req("AC-5")
def test_an_ignored_exception_goes_to_the_logger_at_debug_only(
    caplog: pytest.LogCaptureFixture, ignored_exception: RuntimeError
) -> None:
    hand_to_unraisable_hook(caplog, ignored_exception)

    records = [r for r in caplog.records if r.name == redaction.logger.name]
    assert [r.levelno for r in records] == [logging.DEBUG]


@pytest.mark.req("AC-5")
def test_an_ignored_exception_log_has_no_sentinel(
    caplog: pytest.LogCaptureFixture, ignored_exception: RuntimeError
) -> None:
    hand_to_unraisable_hook(caplog, ignored_exception)

    assert sentinels.leaked(caplog.text) == []


# ----------------------------------------------------------------------------------- AC-5
@pytest.mark.req("AC-5")
def test_main_thread_failure_prints_one_line_and_no_sentinel(
    capsys: pytest.CaptureFixture[str],
) -> None:
    install_excepthooks()

    call_main_hook(secret_error())

    captured = capsys.readouterr()
    assert (captured.err, captured.out) == (FAILURE, "")


@pytest.mark.req("AC-5")
def test_worker_thread_failure_prints_one_line_and_no_sentinel(
    capsys: pytest.CaptureFixture[str],
) -> None:
    install_excepthooks()

    def fail() -> None:
        raise secret_error()

    run_in_worker(fail)

    captured = capsys.readouterr()
    assert (captured.err, captured.out) == (FAILURE, "")


@pytest.mark.req("AC-5")
def test_worker_thread_system_exit_is_ignored_like_the_default_hook(
    capsys: pytest.CaptureFixture[str],
) -> None:
    install_excepthooks()

    def leave() -> None:
        raise SystemExit(3)

    run_in_worker(leave)

    assert capsys.readouterr().err == ""


@pytest.mark.parametrize(
    "where", [pytest.param("main", id="main-thread"), pytest.param("worker", id="worker-thread")]
)
@pytest.mark.req("AC-5")
def test_the_traceback_goes_to_the_logger_at_debug_and_is_redacted(
    caplog: pytest.LogCaptureFixture, where: str
) -> None:
    install_excepthooks()
    caplog.set_level(logging.DEBUG, logger=redaction.logger.name)

    if where == "main":
        call_main_hook(secret_error())
    else:

        def fail() -> None:
            raise secret_error()

        run_in_worker(fail)

    records = [r for r in caplog.records if r.name == redaction.logger.name]
    assert [r.levelno for r in records] == [logging.DEBUG]
    assert "RuntimeError" in records[0].getMessage()
    assert "Traceback" in records[0].getMessage()
    assert sentinels.leaked(caplog.text) == []


@pytest.mark.req("AC-5")
def test_no_traceback_is_produced_when_debug_logging_is_off(
    caplog: pytest.LogCaptureFixture,
) -> None:
    install_excepthooks()
    caplog.set_level(logging.INFO, logger=redaction.logger.name)

    call_main_hook(secret_error())

    assert caplog.records == []


@pytest.mark.req("AC-5")
def test_report_unexpected_failure_works_without_a_traceback(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_unexpected_failure(RuntimeError, None, None)

    assert capsys.readouterr().err == FAILURE


# ----------------------------------------------------------------------------------- AC-8
@pytest.mark.req("AC-8")
def test_ctrl_c_on_the_main_thread_prints_run_cancelled_only(
    capsys: pytest.CaptureFixture[str],
) -> None:
    install_excepthooks()

    call_main_hook(KeyboardInterrupt(sentinels.CLIENT_SECRET))

    captured = capsys.readouterr()
    assert (captured.err, captured.out) == (CANCELLED, "")


@pytest.mark.req("AC-8")
def test_keyboard_interrupt_in_a_worker_prints_run_cancelled_only(
    capsys: pytest.CaptureFixture[str],
) -> None:
    install_excepthooks()

    def interrupt() -> None:
        raise KeyboardInterrupt(sentinels.CLIENT_SECRET)

    run_in_worker(interrupt)

    assert capsys.readouterr().err == CANCELLED


@pytest.mark.req("AC-8")
def test_report_cancelled_prints_the_cancel_line(capsys: pytest.CaptureFixture[str]) -> None:
    report_cancelled()

    assert capsys.readouterr().err == CANCELLED


@pytest.mark.req("AC-8")
def test_a_cancel_does_not_write_a_debug_traceback(caplog: pytest.LogCaptureFixture) -> None:
    install_excepthooks()
    caplog.set_level(logging.DEBUG, logger=redaction.logger.name)

    call_main_hook(KeyboardInterrupt())

    assert caplog.records == []


# ------------------------------------------------------------------------- no stderr to write to
class BrokenStream(io.StringIO):
    def write(self, text: str, /) -> int:
        raise OSError("broken pipe")


@pytest.mark.parametrize(
    "stream",
    [pytest.param(None, id="no-stderr"), pytest.param(BrokenStream(), id="broken-stderr")],
)
def test_a_missing_or_broken_stderr_does_not_raise(
    monkeypatch: pytest.MonkeyPatch, stream: io.StringIO | None
) -> None:
    monkeypatch.setattr(sys, "stderr", stream)

    report_cancelled()
    report_unexpected_failure(RuntimeError, secret_error(), None)


# ------------------------------------------------------------- a failure inside a hook (QUA-27)
# A hook that raises makes CPython print the original exception, unredacted, so nothing may
# escape: the traceback cannot be formatted, ``redact`` fails, the logger fails, stderr fails.
def raising(exc_type: type[BaseException]) -> Callable[..., NoReturn]:
    """A stand-in for a function that fails with ``exc_type``, a sentinel in its message."""

    def raise_it(*args: object, **kwargs: object) -> NoReturn:
        raise exc_type(sentinels.CLIENT_SECRET)

    return raise_it


class StderrThatFails(io.StringIO):
    """A stderr whose write fails with something other than ``OSError`` or ``ValueError``."""

    def __init__(self, exc_type: type[BaseException]) -> None:
        super().__init__()
        self.exc_type = exc_type

    def write(self, text: str, /) -> int:
        raise self.exc_type(sentinels.CLIENT_SECRET)


def break_formatting(
    monkeypatch: pytest.MonkeyPatch, exc_type: type[BaseException] = MemoryError
) -> None:
    monkeypatch.setattr(traceback, "format_exception", raising(exc_type))


def break_redact(
    monkeypatch: pytest.MonkeyPatch, exc_type: type[BaseException] = MemoryError
) -> None:
    monkeypatch.setattr(redaction, "redact", raising(exc_type))


def break_logger(
    monkeypatch: pytest.MonkeyPatch, exc_type: type[BaseException] = MemoryError
) -> None:
    monkeypatch.setattr(redaction.logger, "debug", raising(exc_type))


def break_stderr(
    monkeypatch: pytest.MonkeyPatch, exc_type: type[BaseException] = MemoryError
) -> None:
    monkeypatch.setattr(sys, "stderr", StderrThatFails(exc_type))


def trigger_main_hook(exc: BaseException) -> None:
    sys.excepthook(type(exc), exc, exc.__traceback__)


def trigger_worker_hook(exc: BaseException) -> None:
    threading.excepthook(threading.ExceptHookArgs((type(exc), exc, exc.__traceback__, None)))


def trigger_unraisable_hook(exc: BaseException) -> None:
    sys.unraisablehook(unraisable_args(exc))


def trigger_report(exc: BaseException) -> None:
    report_unexpected_failure(type(exc), exc, exc.__traceback__)


HOOK_TRIGGERS = [
    pytest.param(trigger_main_hook, id="main-thread-hook"),
    pytest.param(trigger_worker_hook, id="worker-thread-hook"),
    pytest.param(trigger_unraisable_hook, id="unraisable-hook"),
]
ENTRY_POINTS = [*HOOK_TRIGGERS, pytest.param(trigger_report, id="report-unexpected-failure")]
# What each entry point may print to stderr, for the two tests that assert on it.
STDERR_OF = {
    trigger_main_hook: FAILURE,
    trigger_worker_hook: FAILURE,
    trigger_unraisable_hook: "",
    trigger_report: FAILURE,
}
FORMAT_OR_REDACT = [
    pytest.param(break_formatting, id="formatting-fails"),
    pytest.param(break_redact, id="redact-fails"),
]
LOGGER_OR_STDERR = [
    pytest.param(break_logger, id="logger-fails"),
    pytest.param(break_stderr, id="stderr-fails"),
]


@pytest.mark.parametrize("breaker", FORMAT_OR_REDACT)
@pytest.mark.parametrize("trigger", ENTRY_POINTS)
@pytest.mark.req("AC-5")
def test_a_failure_while_formatting_or_redacting_does_not_escape(
    monkeypatch: pytest.MonkeyPatch,
    breaker: Callable[[pytest.MonkeyPatch], None],
    trigger: Callable[[BaseException], None],
) -> None:
    install_excepthooks()
    breaker(monkeypatch)

    trigger(secret_error())  # an escaping exception fails the test


@pytest.mark.parametrize("breaker", FORMAT_OR_REDACT)
@pytest.mark.parametrize("trigger", ENTRY_POINTS)
@pytest.mark.req("AC-5")
def test_a_failure_while_formatting_or_redacting_leaves_only_the_fixed_stderr_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    breaker: Callable[[pytest.MonkeyPatch], None],
    trigger: Callable[[BaseException], None],
) -> None:
    install_excepthooks()
    breaker(monkeypatch)

    trigger(secret_error())

    assert capsys.readouterr().err == STDERR_OF[trigger]


@pytest.fixture
def debug_log(caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
    caplog.set_level(logging.DEBUG, logger=redaction.logger.name)
    return caplog


@pytest.mark.parametrize("breaker", FORMAT_OR_REDACT)
@pytest.mark.parametrize("trigger", ENTRY_POINTS)
@pytest.mark.req("AC-5")
def test_an_unavailable_traceback_is_logged_as_the_placeholder(
    monkeypatch: pytest.MonkeyPatch,
    debug_log: pytest.LogCaptureFixture,
    breaker: Callable[[pytest.MonkeyPatch], None],
    trigger: Callable[[BaseException], None],
) -> None:
    install_excepthooks()
    breaker(monkeypatch)

    trigger(secret_error())

    assert redaction.TRACEBACK_UNAVAILABLE in debug_log.text


@pytest.mark.parametrize("breaker", FORMAT_OR_REDACT)
@pytest.mark.parametrize("trigger", ENTRY_POINTS)
@pytest.mark.req("AC-5")
def test_an_unavailable_traceback_leaves_no_sentinel_in_the_log(
    monkeypatch: pytest.MonkeyPatch,
    debug_log: pytest.LogCaptureFixture,
    breaker: Callable[[pytest.MonkeyPatch], None],
    trigger: Callable[[BaseException], None],
) -> None:
    install_excepthooks()
    breaker(monkeypatch)

    trigger(secret_error())

    assert sentinels.leaked(debug_log.text) == []


@pytest.mark.parametrize("breaker", LOGGER_OR_STDERR)
@pytest.mark.parametrize("trigger", HOOK_TRIGGERS)
@pytest.mark.req("AC-5")
def test_a_failing_logger_or_stderr_does_not_escape_a_hook(
    monkeypatch: pytest.MonkeyPatch,
    breaker: Callable[[pytest.MonkeyPatch], None],
    trigger: Callable[[BaseException], None],
) -> None:
    install_excepthooks()
    breaker(monkeypatch)

    trigger(secret_error())  # an escaping exception fails the test


@pytest.mark.parametrize("trigger", HOOK_TRIGGERS)
@pytest.mark.req("AC-5")
def test_a_failing_logger_does_not_change_what_a_hook_prints(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    trigger: Callable[[BaseException], None],
) -> None:
    install_excepthooks()
    break_logger(monkeypatch)

    trigger(secret_error())

    assert capsys.readouterr().err == STDERR_OF[trigger]


# ------------------------------------------- an interrupt or exit inside a hook (QUA-31, D-49)
# The hooks catch ``BaseException`` on purpose: a ``KeyboardInterrupt`` or ``SystemExit`` raised
# inside them would otherwise make CPython print the original exception, unredacted. The log
# filter and its traceback helper catch ``Exception`` only, so Ctrl+C during logging still stops
# the run (the last tests below).
BASE_EXCEPTIONS = [
    pytest.param(KeyboardInterrupt, id="keyboard-interrupt"),
    pytest.param(SystemExit, id="system-exit"),
]


def assert_nothing_escapes(trigger: Callable[[BaseException], None]) -> None:
    """Run ``trigger``; whatever escapes it is a named failure, not a crash of the test run."""
    try:
        trigger(secret_error())
    except BaseException as escaped:
        pytest.fail(f"{type(escaped).__name__} escaped {trigger.__name__}")


@pytest.mark.parametrize("exc_type", BASE_EXCEPTIONS)
@pytest.mark.parametrize("breaker", [*FORMAT_OR_REDACT, *LOGGER_OR_STDERR])
@pytest.mark.parametrize("trigger", HOOK_TRIGGERS)
@pytest.mark.req("AC-5")
def test_a_base_exception_inside_a_hook_does_not_escape(
    monkeypatch: pytest.MonkeyPatch,
    breaker: Callable[[pytest.MonkeyPatch, type[BaseException]], None],
    trigger: Callable[[BaseException], None],
    exc_type: type[BaseException],
) -> None:
    install_excepthooks()
    breaker(monkeypatch, exc_type)

    assert_nothing_escapes(trigger)


FILTERED_LOGGER = "gmail_pdf.filter_under_test"


@pytest.fixture
def filtered_log() -> Iterator[io.StringIO]:
    """The output of a logger whose only handler carries the redacting filter."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(redaction.RedactingFilter())
    log = logging.getLogger(FILTERED_LOGGER)
    log.propagate = False
    log.addHandler(handler)
    yield stream
    log.removeHandler(handler)


@pytest.mark.parametrize("breaker", FORMAT_OR_REDACT)
@pytest.mark.req("AC-3", "AC-8")
def test_an_interrupt_while_sanitising_a_record_still_stops_the_logging_call(
    monkeypatch: pytest.MonkeyPatch,
    filtered_log: io.StringIO,
    breaker: Callable[[pytest.MonkeyPatch, type[BaseException]], None],
) -> None:
    breaker(monkeypatch, KeyboardInterrupt)

    with pytest.raises(KeyboardInterrupt):
        try:
            raise secret_error()
        except RuntimeError:
            logging.getLogger(FILTERED_LOGGER).exception("step failed")


# ----------------------------------- what the filter falls back to when it fails (QUA-27, QUA-32)
# Kept by the fallback, ``args`` would make ``Handler.handleError`` print them raw and
# ``stack_info`` would be appended raw; no other test builds a record that carries either.
FALLBACK_FIELDS = [
    pytest.param({"args": (sentinels.CLIENT_SECRET,)}, id="args"),
    pytest.param(
        {"stack_info": f"Stack (most recent call last):\n  {sentinels.CLIENT_SECRET}"},
        id="stack-info",
    ),
]


@pytest.mark.parametrize("field", FALLBACK_FIELDS)
@pytest.mark.req("AC-3")
def test_the_filter_fallback_clears_args_and_stack_info(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    filtered_log: io.StringIO,
    field: dict[str, object],
) -> None:
    monkeypatch.setattr(logging, "raiseExceptions", True)  # handleError prints what it could not
    break_redact(monkeypatch)
    record = logging.LogRecord(
        FILTERED_LOGGER, logging.WARNING, __file__, 1, "value %s", None, None
    )
    vars(record).update(field)

    logging.getLogger(FILTERED_LOGGER).handle(record)

    assert sentinels.leaked(filtered_log.getvalue() + capsys.readouterr().err) == []
