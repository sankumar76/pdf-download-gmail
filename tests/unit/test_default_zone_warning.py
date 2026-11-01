"""PGD-84 AC-10 (droppable): the one stderr line that says dates use Asia/Kolkata.

Every row of the AC-10 group is here, and nothing else asserts the line (the fallback tests in
``test_default_zone_fallback.py`` pass with or without it). To drop AC-10: delete this file,
``ZONE_FALLBACK_WARNING_TEMPLATE`` in ``domain/messages.py`` and the one branch in
``domain/validation.py`` that adds the row. The expected text is a literal from the story
(ux-expert, PGD-1 c.10409). "Today" is a clock frozen at 2026-02-15 12:00 UTC.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from gmail_pdf.cli import main as cli_main
from gmail_pdf.domain import messages
from gmail_pdf.infra import tz as tz_module
from tests.fakes.fake_time import FixedInstantClock
from tests.support import system_zone
from tests.support.cli_inprocess import must_not_be_called, use_hook
from tests.support.mailboxes import MESSAGES_IN_RANGE_LINE, RANGE_ARGS, write_edge_mailbox
from tests.support.validation_inputs import FUTURE_END, check

pytestmark = [pytest.mark.req("FR-008", "FR-015", "AC-10")]

ZONE_LINE = (
    "The system time zone could not be identified, so dates use Asia/Kolkata. "
    "Use --tz to change it."
)
FUTURE_END_LINE = f"warning: {FUTURE_END}"
NO_TZ_ARGS = RANGE_ARGS[:4]
FUTURE_ARGS = ["--start", "2026-01-01", "--end", "2026-03-01"]  # after the frozen 2026-02-15


@pytest.fixture(autouse=True)
def _no_hook_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every test in real mode, whatever the developer's shell holds."""
    monkeypatch.delenv(ENV_FAKE_MAILBOX, raising=False)
    monkeypatch.delenv(ENV_TESTING, raising=False)


@pytest.fixture(autouse=True)
def _frozen_today(monkeypatch: pytest.MonkeyPatch) -> None:
    """Today is 2026-02-15 (12:00 UTC), whatever the machine's date and zone are."""
    clock = FixedInstantClock(datetime(2026, 2, 15, 12, 0, tzinfo=timezone.utc))
    monkeypatch.setattr(cli_main, "SystemClock", lambda: clock)


@pytest.fixture
def system_zone_unidentified(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        tz_module.tzlocal, "get_localzone_name", system_zone.raising(LookupError("no zone key"))
    )


# ----------------------------------------------------------------------- at validate level
def test_validate_adds_the_zone_line_once_for_the_fallback() -> None:
    result = check(end="2026-01-10", zone=None)  # a past end: nothing else to warn about

    assert (result.errors, result.warnings) == ((), (ZONE_LINE,))


def test_validate_puts_the_zone_line_before_the_future_end_warning() -> None:
    result = check(zone=None)  # the default end, 2026-01-31, is after the frozen 2026-01-15

    assert result.warnings == (ZONE_LINE, FUTURE_END)


@pytest.mark.parametrize(
    ("start", "end", "zone"),
    [
        pytest.param("2026-01-01", "2026-01-10", "UTC", id="tz-given"),
        pytest.param("2026-01-01", "2026-01-10", "Asia/Kolkata", id="tz-given-is-the-fallback"),
        pytest.param("x", "2026-01-10", None, id="rejected-input"),
        pytest.param("2026-02-01", "2026-01-10", None, id="reversed-range"),
    ],
)
def test_validate_adds_no_zone_line_otherwise(start: str, end: str, zone: str | None) -> None:
    result = check(start=start, end=end, zone=zone)

    assert ZONE_LINE not in result.warnings
    assert result.warnings == ()


# ------------------------------------------------------------------------ through the CLI
def test_the_test_hook_run_prints_the_line_once_on_stderr_and_leaves_stdout_alone(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    system_zone_unidentified: None,
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))
    assert cli_main.main(RANGE_ARGS) == 0
    explicit = capsys.readouterr()

    code = cli_main.main(NO_TZ_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (
        0,
        MESSAGES_IN_RANGE_LINE,
        f"warning: {ZONE_LINE}\n",
    )
    assert captured.out == explicit.out
    assert explicit.err == ""


def test_the_real_mode_run_prints_the_line_then_the_fixed_error_line(
    capsys: pytest.CaptureFixture[str], system_zone_unidentified: None
) -> None:
    code = cli_main.main(NO_TZ_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (
        3,
        "",
        f"warning: {ZONE_LINE}\n{messages.SIGN_IN_UNAVAILABLE_LINE}\n",
    )


def test_the_zone_line_comes_before_the_future_end_warning_and_the_run_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    system_zone_unidentified: None,
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main(FUTURE_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.err) == (0, f"warning: {ZONE_LINE}\n{FUTURE_END_LINE}\n")
    assert captured.out == "Messages in range: 3\n"  # the run's own output, not the warning's


# --------------------------------------------------------------------- the not-printed cases
def test_no_line_when_tz_is_given(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", must_not_be_called)
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main(RANGE_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, MESSAGES_IN_RANGE_LINE, "")


def test_no_line_when_the_system_zone_resolves(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", system_zone.reporting("UTC"))
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main(NO_TZ_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.err) == (0, "")


def test_no_line_for_rejected_input(
    capsys: pytest.CaptureFixture[str], system_zone_unidentified: None
) -> None:
    code = cli_main.main(["--start", "x", "--end", "2026-01-31"])

    captured = capsys.readouterr()
    assert (code, captured.err) == (
        2,
        "error: --start: Enter the date as YYYY-MM-DD, for example 2026-01-31.\n",
    )


@pytest.mark.usefixtures("no_kolkata_data")
def test_no_line_in_the_broken_install_case(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        tz_module.tzlocal, "get_localzone_name", system_zone.raising(LookupError("no zone key"))
    )
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)

    code = cli_main.main(NO_TZ_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.err) == (1, f"{messages.UNEXPECTED_FAILURE_LINE}\n")


@pytest.mark.parametrize(
    "argv",
    [pytest.param(["--help"], id="help"), pytest.param([], id="neither-date")],
)
def test_no_line_for_help_or_neither_date(
    capsys: pytest.CaptureFixture[str], system_zone_unidentified: None, argv: list[str]
) -> None:
    code = cli_main.main(argv)

    captured = capsys.readouterr()
    assert (code, captured.err) == (0, "")
    assert "usage:" in captured.out
