"""PGD-16 AC-1..AC-6 and AC-9 through ``cli.main.main`` in this process: bad input is rejected.

Every rejection exits 2 before ``build_deps`` is reached, so no credential is read, no folder or
file is created and no Google call is made, in real mode and on the test hook alike. The
subprocess versions are in ``tests/e2e/test_invalid_input.py``. The expected lines are literals
from the story. "Today" is a clock frozen at 2026-02-15 12:00 UTC.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfoNotFoundError

import pytest

from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from gmail_pdf.cli import main as cli_main
from gmail_pdf.infra import tz as tz_module
from tests.fakes.fake_time import FixedInstantClock
from tests.support import sentinels
from tests.support.cli_inprocess import must_not_be_called, use_hook
from tests.support.mailboxes import RANGE_ARGS, write_edge_mailbox

pytestmark = pytest.mark.req("FR-008", "FR-012")

START_FORMAT = "error: --start: Enter the date as YYYY-MM-DD, for example 2026-01-31."
END_FORMAT = "error: --end: Enter the date as YYYY-MM-DD, for example 2026-01-31."
START_BOUNDS = "error: --start: Enter a date from 1970-01-02 to 9999-12-30."
END_BOUNDS = "error: --end: Enter a date from 1970-01-02 to 9999-12-30."
ZONE_ERROR = "error: --tz: Unknown time zone. Use an IANA name such as Asia/Kolkata."
REVERSED = (
    "error: Start date must be on or before the end date. (--start 2026-03-31 --end 2026-01-01)"
)


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


# ------------------------------------------------------------------------- usage errors
@pytest.mark.req("AC-1", "AC-2", "AC-4", "AC-5", "AC-6", "AC-9")
@pytest.mark.parametrize(
    ("argv", "lines"),
    [
        pytest.param(["--start", "2026-01-01"], [END_FORMAT], id="only-start"),
        pytest.param(["--end", "2026-01-31"], [START_FORMAT], id="only-end"),
        pytest.param(
            ["--start", "2026-1-1", "--end", "2026-01-31"], [START_FORMAT], id="bad-start"
        ),
        pytest.param(["--start", "2026-01-01", "--end", "31/01/2026"], [END_FORMAT], id="bad-end"),
        pytest.param(
            ["--start", "1970-01-01", "--end", "2026-01-31", "--tz", "UTC"],
            [START_BOUNDS],
            id="start-below-the-floor",
        ),
        pytest.param(
            ["--start", "2026-01-01", "--end", "9999-12-31", "--tz", "UTC"],
            [END_BOUNDS],
            id="end-above-the-ceiling",
        ),
        pytest.param(
            ["--start", "1960-01-01", "--end", "1950-01-01", "--tz", "UTC"],
            [START_BOUNDS, END_BOUNDS],
            id="both-out-of-bounds-no-order-line",
        ),
        pytest.param(
            ["--start", "2026-03-31", "--end", "2026-01-01", "--tz", "UTC"],
            [REVERSED],
            id="reversed-range",
        ),
        pytest.param(
            ["--start", "2026-01-01", "--end", "2026-01-31", "--tz", "Mars/Olympus"],
            [ZONE_ERROR],
            id="unknown-zone",
        ),
        pytest.param(
            ["--start", "2026-1-1", "--end", "2026-01-31", "--tz", "Mars/Olympus"],
            [START_FORMAT, ZONE_ERROR],
            id="bad-start-and-bad-zone",
        ),
        pytest.param(
            ["--start", "2026-03-31", "--end", "2026-01-01", "--tz", "Mars/Olympus"],
            [REVERSED, ZONE_ERROR],
            id="reversed-and-bad-zone",
        ),
    ],
)
def test_invalid_input_exits_two_in_real_mode_before_build_deps_is_reached(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    argv: list[str],
    lines: list[str],
) -> None:
    # Real mode: the autouse fixture removed both hook variables, so ``build_deps`` would end
    # in exit 3. It fails the test if it is called at all.
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)
    monkeypatch.setattr(cli_main.runner, "run", must_not_be_called)

    code = cli_main.main(argv)

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, "".join(f"{line}\n" for line in lines), "")


# The full matrix of malformed dates (PERF-17): the end-to-end file keeps two of these forms as
# child processes; every form, for both dates and both modes, is checked here.
MALFORMED_DATES = [
    pytest.param("2026-1-5", id="no-zero-padding"),
    pytest.param("2026/01/05", id="slashes"),
    pytest.param("05-01-2026", id="day-first"),
    pytest.param("2026-02-30", id="30-february"),
    pytest.param("", id="empty"),
    pytest.param("   ", id="spaces"),
    pytest.param("20260105", id="basic-format"),
    pytest.param("٢٠٢٦-٠١-٠٥", id="arabic-indic-digits"),
]


@pytest.mark.req("AC-1", "AC-6")
@pytest.mark.parametrize("hook", [True, False], ids=["test-hook", "real-mode"])
@pytest.mark.parametrize(
    ("field", "line"),
    [pytest.param("start", START_FORMAT, id="start"), pytest.param("end", END_FORMAT, id="end")],
)
@pytest.mark.parametrize("text", MALFORMED_DATES)
def test_a_malformed_date_gets_the_format_line_and_nothing_runs(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    text: str,
    field: str,
    line: str,
    hook: bool,
) -> None:
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    if hook:
        use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))
    else:
        monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)
    start, end = (text, "2026-01-31") if field == "start" else ("2026-01-01", text)

    code = cli_main.main(["--start", start, "--end", end, "--tz", "UTC"])

    captured = capsys.readouterr()
    created = list(workdir.iterdir())
    assert (code, captured.err, captured.out, created) == (2, line + "\n", "", [])


@pytest.mark.req("AC-2", "AC-4")
@pytest.mark.parametrize(
    ("argv", "line"),
    [
        pytest.param(
            ["--start", "2026-01-01", "--end", "2026-01-31", "--tz", "Mars/Olympus"],
            ZONE_ERROR,
            id="unknown-zone",
        ),
        pytest.param(
            ["--start", "2026-03-31", "--end", "2026-01-01", "--tz", "UTC"],
            REVERSED,
            id="end-before-start",
        ),
    ],
)
def test_a_bad_zone_or_range_order_exits_two_on_the_test_hook_too(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    argv: list[str],
    line: str,
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main(argv)

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, line + "\n", "")


@pytest.mark.req("AC-4")
@pytest.mark.parametrize(
    "zone",
    ["Mars/Olympus", "IST", "", "Asia/Kolkata ", "Asia\\Kolkata", "utc", "asia/kolkata"],
)
@pytest.mark.parametrize("hook", [True, False], ids=["test-hook", "real-mode"])
def test_a_zone_outside_the_iana_set_is_rejected_as_written_in_both_modes(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    zone: str,
    hook: bool,
) -> None:
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    if hook:
        use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))
    else:
        monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)

    code = cli_main.main(["--start", "2026-01-01", "--end", "2026-01-31", "--tz", zone])

    captured = capsys.readouterr()
    created = list(workdir.iterdir())
    assert (code, captured.err, captured.out, created) == (2, ZONE_ERROR + "\n", "", [])


def _empty_name() -> str:
    return ""


def _not_an_iana_name() -> str:
    return "Mars/Olympus"


def _raising(error: Exception) -> Callable[[], str]:
    def lookup() -> str:
        raise error

    return lookup


# Every class ``tzlocal`` can fail with when the system zone is unresolved (PGD-16 AC-4, G6 O1):
# a registry without a zone key, an unknown name, an unreadable source and a registry value of
# the wrong type. Each class has its own row, so dropping one from the ``except`` fails a row.
SYSTEM_ZONE_FAILURES = [
    pytest.param(_empty_name, id="empty-name"),
    pytest.param(_not_an_iana_name, id="not-an-iana-name"),
    pytest.param(_raising(LookupError("no zone key")), id="lookup-error"),
    pytest.param(_raising(ZoneInfoNotFoundError("no zone")), id="zone-info-not-found"),
    pytest.param(_raising(ValueError("bad zone")), id="value-error"),
    pytest.param(_raising(OSError("no zone")), id="os-error"),
    pytest.param(_raising(AttributeError("no encode")), id="attribute-error"),
    pytest.param(_raising(TypeError("not a string")), id="type-error"),
]


@pytest.mark.req("AC-4")
@pytest.mark.parametrize("lookup", SYSTEM_ZONE_FAILURES)
def test_an_unusable_system_zone_without_tz_gets_the_zone_sentence(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, lookup: Callable[[], str]
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lookup)
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)

    code = cli_main.main(["--start", "2026-01-01", "--end", "2026-01-31"])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, ZONE_ERROR + "\n", "")


@pytest.mark.req("AC-4", "AC-5")
def test_an_unresolved_system_zone_comes_after_the_date_line(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", _raising(LookupError("no key")))
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)

    code = cli_main.main(["--start", "x", "--end", "2026-01-31"])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, f"{START_FORMAT}\n{ZONE_ERROR}\n", "")


@pytest.mark.req("AC-3")
def test_the_future_warning_is_not_printed_for_invalid_input(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = cli_main.main(["--start", "2026-01-01", "--end", "9999-12-31", "--tz", "UTC"])

    assert (code, capsys.readouterr().err) == (2, END_BOUNDS + "\n")


@pytest.mark.req("AC-6")
@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["--sta", "2026-01-01", "--end", "2026-01-31"], id="abbreviated-start"),
        pytest.param(["--start", "2026-01-01", "--en", "2026-01-31"], id="abbreviated-end"),
        pytest.param([*RANGE_ARGS[:4], "--t", "UTC"], id="abbreviated-tz"),
        pytest.param(["--star", "2026-01-01", "--end", "2026-01-31"], id="one-letter-short"),
    ],
)
def test_an_abbreviated_flag_is_an_unknown_flag_and_nothing_runs(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, argv: list[str]
) -> None:
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)
    monkeypatch.setattr(cli_main.runner, "run", must_not_be_called)

    code = cli_main.main(argv)

    captured = capsys.readouterr()
    assert (code, captured.out) == (2, "")
    assert "unrecognized arguments" in captured.err  # argparse's own wording (issue #23)


@pytest.mark.req("AC-6")
def test_invalid_input_logs_only_the_fixed_lines_and_sets_up_no_log_handler(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)
    handlers_before = list(logging.getLogger().handlers)

    with caplog.at_level(logging.DEBUG):
        cli_main.main(["--start", sentinels.CLIENT_SECRET, "--end", "2026-01-31", "--tz", "UTC"])

    assert [r.getMessage() for r in caplog.records if r.name == "gmail_pdf.cli.main"] == [
        START_FORMAT
    ]
    assert all(record.exc_info is None for record in caplog.records)
    assert sentinels.leaked(caplog.text) == []
    assert list(logging.getLogger().handlers) == handlers_before


def test_a_bad_value_is_never_echoed(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))
    secret_zone = f"Zone/{sentinels.CLIENT_SECRET}"

    cli_main.main(["--start", "2026-01-01", "--end", "2026-01-31", "--tz", secret_zone])
    cli_main.main(["--start", sentinels.REFRESH_TOKEN, "--end", "2026-01-31"])

    captured = capsys.readouterr()
    assert sentinels.leaked(captured.err + captured.out) == []
