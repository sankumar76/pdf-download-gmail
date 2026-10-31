"""PGD-17 AC-4 through ``cli.main.main`` in this process: a failed list call is a failed run.

The fake-mailbox hook cannot carry a scripted fault and a child process cannot reach the real
gateway (``build_deps`` does not build it), so both legs call ``main`` with ``build_deps``
replaced by a function that returns the ``Deps`` under test:

* leg (a): ``FakeGmail`` failing ``list_message_ids`` with HTTP 503 on every call;
* leg (b): the real ``GmailGateway`` over six scripted 503 answers (the ``Rig`` of
  ``tests/support/gateway_rig.py``), so the retry helper really logs five records.

The stderr rule (C40, GitHub #40): retry records are log content, not user output, until the run
log exists. Pytest keeps a handler on the root logger, so ``logging.lastResort`` (the stderr
handler Python falls back to) would never fire in these tests and "no ``Retrying`` line" would
pass whether or not the rule is implemented. ``Run`` therefore removes the root handlers right
before it calls ``main``, in the same test phase as the logging that follows (pytest adds its
handlers again at the start of each phase), which makes the check real.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType

import pytest

from gmail_pdf import redaction
from gmail_pdf.app.ports import Deps, GmailPort
from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from gmail_pdf.cli import main as cli_main
from gmail_pdf.domain.errors import RetryExhaustedError
from gmail_pdf.infra import tz as tz_module
from tests.fakes.fake_gmail import FakeGmail
from tests.fakes.fake_time import FixedInstantClock
from tests.support import sentinels
from tests.support.gateway_rig import Rig, error
from tests.support.mailboxes import RANGE_ARGS, edge_mailbox

pytestmark = pytest.mark.req("FR-016", "EC-06", "AC-4")

FAILURE_LINE = "error: unexpected failure, see the run log"
FUTURE_END_WARNING = "warning: End date is in the future. Only mail received so far is included."
FUTURE_END_ARGS = ["--start", "2026-01-01", "--end", "2099-12-31", "--tz", "Asia/Kolkata"]
RETRY_LOGGER = "gmail_pdf.infra.retry"


@pytest.fixture(autouse=True)
def _real_mode_and_a_frozen_today(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Hook variables off, today frozen at 2026-02-15, and an empty working directory."""
    monkeypatch.delenv(ENV_FAKE_MAILBOX, raising=False)
    monkeypatch.delenv(ENV_TESTING, raising=False)
    clock = FixedInstantClock(datetime(2026, 2, 15, 12, 0, tzinfo=timezone.utc))
    monkeypatch.setattr(cli_main, "SystemClock", lambda: clock)
    monkeypatch.chdir(tmp_path)


@dataclass(frozen=True)
class Outcome:
    code: int
    out: str
    err: str


class Run:
    """``main`` run once with ``gmail`` behind ``build_deps``; what it printed and raised."""

    def __init__(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        gmail: GmailPort,
        argv: list[str],
        *,
        keep_root_handlers: bool = False,
    ) -> None:
        if not keep_root_handlers:
            monkeypatch.setattr(logging.getLogger(), "handlers", [])
        deps = Deps(gmail=gmail, resolve_zone=tz_module.resolve_zone)
        monkeypatch.setattr(cli_main, "build_deps", lambda: deps)
        self.escaped: list[type[BaseException]] = []
        real_report = redaction.report_unexpected_failure

        def spy(
            exc_type: type[BaseException],
            exc_value: BaseException | None,
            exc_traceback: TracebackType | None,
        ) -> None:
            self.escaped.append(exc_type)
            real_report(exc_type, exc_value, exc_traceback)

        monkeypatch.setattr(redaction, "report_unexpected_failure", spy)
        code = cli_main.main(argv)
        captured = capsys.readouterr()
        self.outcome = Outcome(code, captured.out, captured.err)


def failing_fake() -> FakeGmail:
    fake = edge_mailbox()
    fake.fail_with_http("list_message_ids", 503, times=None)
    return fake


def six_503s() -> Rig:
    return Rig(*[error(503)] * 6)


def created_in_cwd() -> list[str]:
    return sorted(path.name for path in Path.cwd().rglob("*"))


# ------------------------------------------------------------------ leg (a): through FakeGmail
@pytest.fixture
def leg_a(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> tuple[Run, FakeGmail]:
    fake = failing_fake()
    return Run(monkeypatch, capsys, fake, RANGE_ARGS), fake


def test_leg_a_the_run_ends_with_exit_code_one(leg_a: tuple[Run, FakeGmail]) -> None:
    assert leg_a[0].outcome.code == 1


def test_leg_a_stdout_is_exactly_empty(leg_a: tuple[Run, FakeGmail]) -> None:
    assert leg_a[0].outcome.out == ""


def test_leg_a_stderr_is_the_one_error_line(leg_a: tuple[Run, FakeGmail]) -> None:
    assert leg_a[0].outcome.err == FAILURE_LINE + "\n"


def test_leg_a_the_list_call_was_made_once_and_no_message_was_read(
    leg_a: tuple[Run, FakeGmail],
) -> None:
    assert [call.method for call in leg_a[1].calls] == ["list_message_ids"]


def test_leg_a_the_run_is_not_reported_as_empty(leg_a: tuple[Run, FakeGmail]) -> None:
    surfaces = leg_a[0].outcome.out + leg_a[0].outcome.err

    assert [
        text for text in ("No PDFs found", "0 PDFs found.", "Messages in range") if text in surfaces
    ] == []


def test_leg_a_no_file_or_folder_is_created(leg_a: tuple[Run, FakeGmail]) -> None:
    assert created_in_cwd() == []


def test_leg_a_after_a_future_end_warning_stderr_is_the_warning_then_the_error_line(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = Run(monkeypatch, capsys, failing_fake(), FUTURE_END_ARGS)

    assert run.outcome == Outcome(1, "", FUTURE_END_WARNING + "\n" + FAILURE_LINE + "\n")


# ------------------------------------------------------- leg (b): through the real gateway
@pytest.fixture
def leg_b(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> tuple[Run, Rig]:
    rig = six_503s()
    return Run(monkeypatch, capsys, rig.gateway, RANGE_ARGS), rig


def test_leg_b_six_requests_were_sent(leg_b: tuple[Run, Rig]) -> None:
    assert len(leg_b[1].requests) == 6


def test_leg_b_five_waits_stand_for_the_five_retry_records(leg_b: tuple[Run, Rig]) -> None:
    assert leg_b[1].sleeper.delays == [1.0, 2.0, 4.0, 8.0, 16.0]


def test_leg_b_the_exhaustion_error_reaches_main(leg_b: tuple[Run, Rig]) -> None:
    assert leg_b[0].escaped == [RetryExhaustedError]


def test_leg_b_the_run_ends_with_exit_code_one_and_empty_stdout(leg_b: tuple[Run, Rig]) -> None:
    assert (leg_b[0].outcome.code, leg_b[0].outcome.out) == (1, "")


def test_leg_b_stderr_is_exactly_the_one_error_line(leg_b: tuple[Run, Rig]) -> None:
    assert leg_b[0].outcome.err == FAILURE_LINE + "\n"


def test_leg_b_no_retry_notice_reaches_stderr(leg_b: tuple[Run, Rig]) -> None:
    assert "Retrying" not in leg_b[0].outcome.err


def test_leg_b_no_file_or_folder_is_created(leg_b: tuple[Run, Rig]) -> None:
    assert created_in_cwd() == []


def test_leg_b_after_a_future_end_warning_stderr_is_the_warning_then_the_error_line(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = Run(monkeypatch, capsys, six_503s().gateway, FUTURE_END_ARGS)

    assert run.outcome == Outcome(1, "", FUTURE_END_WARNING + "\n" + FAILURE_LINE + "\n")


# ----------------------------------------------- what the rule does not touch (PGD-13, PGD-15)
def test_the_five_retry_records_are_still_logged_at_warning_for_a_future_run_log(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.DEBUG):
        Run(monkeypatch, capsys, six_503s().gateway, RANGE_ARGS, keep_root_handlers=True)

    retries = [r for r in caplog.records if r.name == RETRY_LOGGER]
    assert [(r.levelno, r.getMessage()) for r in retries] == [
        (logging.WARNING, f"Retrying list_message_ids: attempt {n} of 6 after {delay} s")
        for n, delay in ((2, "1.0"), (3, "2.0"), (4, "4.0"), (5, "8.0"), (6, "16.0"))
    ]


def test_running_main_twice_adds_the_handler_once(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    Run(monkeypatch, capsys, failing_fake(), RANGE_ARGS)
    Run(monkeypatch, capsys, failing_fake(), RANGE_ARGS)

    handlers = logging.getLogger(RETRY_LOGGER).handlers
    assert [type(handler) for handler in handlers] == [logging.NullHandler]


def test_another_logger_keeps_the_redacted_last_resort_fallback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    Run(monkeypatch, capsys, failing_fake(), RANGE_ARGS)
    redaction.register_secret(sentinels.CLIENT_SECRET)

    logging.getLogger("some.library").warning("token=%s", sentinels.CLIENT_SECRET)

    err = capsys.readouterr().err
    assert err.startswith("token=")
    assert sentinels.leaked(err) == []


def test_a_warning_from_another_gmail_pdf_logger_still_reaches_stderr(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    Run(monkeypatch, capsys, failing_fake(), RANGE_ARGS)

    logging.getLogger("gmail_pdf.infra.paths").warning("Could not remove temporary file %s", "x")

    assert capsys.readouterr().err == "Could not remove temporary file x\n"
