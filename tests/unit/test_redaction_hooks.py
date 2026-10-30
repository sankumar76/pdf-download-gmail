"""PGD-13 AC-5 and AC-8: the excepthook installers, the unexpected-failure and cancel lines."""

from __future__ import annotations

import io
import logging
import sys
import threading
import types
from collections.abc import Callable

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
