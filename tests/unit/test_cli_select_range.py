"""PGD-15 AC-5, AC-6 and PGD-16 AC-1..AC-6, AC-9 through ``cli.main.main`` in this process.

The subprocess versions are in ``tests/e2e/test_select_range.py`` and
``tests/e2e/test_invalid_input.py``. Here the exit codes, the stderr lines, the log records, the
order "validate, then ``build_deps``" and the "no fall-through" rule are checked with the real
code and a monkeypatched environment. "Today" is a clock frozen at 2026-02-15 12:00 UTC.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import NoReturn
from zoneinfo import ZoneInfoNotFoundError, available_timezones

import pytest

from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from gmail_pdf.cli import main as cli_main
from gmail_pdf.domain import messages
from gmail_pdf.domain.models import RunResult, RunSummary
from gmail_pdf.infra import tz as tz_module
from tests.fakes.fake_time import FixedInstantClock
from tests.support import sentinels
from tests.support.mailboxes import MESSAGES_IN_RANGE_LINE, RANGE_ARGS, write_edge_mailbox

pytestmark = pytest.mark.req("FR-008", "FR-012")

START_FORMAT = "error: --start: Enter the date as YYYY-MM-DD, for example 2026-01-31."
END_FORMAT = "error: --end: Enter the date as YYYY-MM-DD, for example 2026-01-31."
START_BOUNDS = "error: --start: Enter a date from 1970-01-02 to 9999-12-30."
END_BOUNDS = "error: --end: Enter a date from 1970-01-02 to 9999-12-30."
ZONE_ERROR = "error: --tz: Unknown time zone. Use an IANA name such as Asia/Kolkata."
REVERSED = (
    "error: Start date must be on or before the end date. (--start 2026-03-31 --end 2026-01-01)"
)
FUTURE_END = "warning: End date is in the future. Only mail received so far is included."


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


def use_hook(monkeypatch: pytest.MonkeyPatch, path: Path, testing: str | None = "1") -> None:
    monkeypatch.setenv(ENV_FAKE_MAILBOX, str(path))
    if testing is not None:
        monkeypatch.setenv(ENV_TESTING, testing)


# ----------------------------------------------------------------------------------- AC-5
@pytest.mark.req("AC-5")
def test_a_range_prints_the_interim_count_and_returns_zero(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main(RANGE_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, MESSAGES_IN_RANGE_LINE, "")


@pytest.mark.req("AC-5", "AC-10")
def test_without_tz_the_system_zone_is_used(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lambda: "Asia/Kolkata")
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main(RANGE_ARGS[:4])

    assert (code, capsys.readouterr().out) == (0, MESSAGES_IN_RANGE_LINE)


# ----------------------------------------------------------------------------------- AC-6
def _must_not_be_called(*_args: object) -> NoReturn:
    """A stub that fails the test when reached: ``build_deps``, the run or a zone lookup."""
    raise AssertionError("this call must not be reached in this test")


BUILD_FAILURES = [
    pytest.param(None, None, messages.SIGN_IN_UNAVAILABLE_LINE, 3, id="real-mode"),
    pytest.param("good", None, messages.FAKE_MAILBOX_HOOK_REFUSED_LINE, 1, id="hook-refused"),
    pytest.param("absent", "1", messages.FAKE_MAILBOX_UNREADABLE_LINE, 1, id="file-missing"),
]


@pytest.mark.req("AC-6")
@pytest.mark.parametrize(("mailbox", "testing", "line", "exit_code"), BUILD_FAILURES)
def test_build_failures_print_one_fixed_line_with_the_right_exit_code(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mailbox: str | None,
    testing: str | None,
    line: str,
    exit_code: int,
) -> None:
    if mailbox == "good":
        use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"), testing)
    elif mailbox == "absent":
        use_hook(monkeypatch, tmp_path / f"{sentinels.CLIENT_SECRET}.json", testing)

    code = cli_main.main(RANGE_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (exit_code, line + "\n", "")


@pytest.mark.req("AC-6")
def test_the_not_importable_case_has_its_own_line_and_exits_one(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from gmail_pdf import bootstrap

    monkeypatch.setattr(bootstrap, "_FAKE_MODULE", "tests.fakes.does_not_exist")
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main(RANGE_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (
        1,
        messages.FAKE_MAILBOX_NOT_IMPORTABLE_LINE + "\n",
        "",
    )


@pytest.mark.req("AC-6")
def test_a_hook_failure_logs_only_the_fixed_line_without_exception_details(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    path = tmp_path / f"{sentinels.CLIENT_SECRET}.json"
    path.write_text(f'{{"note": "{sentinels.REFRESH_TOKEN}"', encoding="utf-8")  # bad JSON
    use_hook(monkeypatch, path)

    with caplog.at_level(logging.DEBUG):
        cli_main.main(RANGE_ARGS)

    assert [r.getMessage() for r in caplog.records if r.name == "gmail_pdf.cli.main"] == [
        messages.FAKE_MAILBOX_UNREADABLE_LINE
    ]
    assert all(record.exc_info is None for record in caplog.records)
    assert sentinels.leaked(caplog.text) == []
    assert str(path) not in caplog.text


@pytest.mark.req("AC-6")
@pytest.mark.parametrize(
    "case",
    [
        pytest.param("refused", id="hook-refused"),
        pytest.param("unusable", id="fake-file-unusable"),
    ],
)
def test_a_hook_failure_is_final_the_run_never_starts_and_real_mode_is_not_tried(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, case: str
) -> None:
    builds: list[int] = []
    real_build = cli_main.build_deps
    monkeypatch.setattr(cli_main, "build_deps", lambda: builds.append(1) or real_build())
    monkeypatch.setattr(cli_main.runner, "run", _must_not_be_called)
    use_hook(
        monkeypatch,
        tmp_path / "absent.json" if case == "unusable" else write_edge_mailbox(tmp_path / "m.json"),
        "1" if case == "unusable" else None,
    )

    code = cli_main.main(RANGE_ARGS)

    assert (code, len(builds)) == (1, 1)


@pytest.mark.req("AC-5", "FR-043")
def test_a_cancelled_run_prints_the_notice_and_exits_one(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))
    monkeypatch.setattr(cli_main.runner, "run", lambda *_args: RunSummary(RunResult.CANCELLED))

    code = cli_main.main(RANGE_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (1, "Run cancelled\n", "")


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
    monkeypatch.setattr(cli_main, "build_deps", _must_not_be_called)
    monkeypatch.setattr(cli_main.runner, "run", _must_not_be_called)

    code = cli_main.main(argv)

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, "".join(f"{line}\n" for line in lines), "")


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
    if hook:
        use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))
    else:
        monkeypatch.setattr(cli_main, "build_deps", _must_not_be_called)

    code = cli_main.main(["--start", "2026-01-01", "--end", "2026-01-31", "--tz", zone])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, ZONE_ERROR + "\n", "")


@pytest.mark.req("AC-4")
@pytest.mark.parametrize("zone", ["UTC", "Asia/Kolkata"])
def test_a_zone_in_the_iana_set_is_accepted(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    zone: str,
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main(["--start", "2026-01-01", "--end", "2026-01-31", "--tz", zone])

    assert (code, capsys.readouterr().err) == (0, "")


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
    monkeypatch.setattr(cli_main, "build_deps", _must_not_be_called)

    code = cli_main.main(["--start", "2026-01-01", "--end", "2026-01-31"])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, ZONE_ERROR + "\n", "")


@pytest.mark.req("AC-4", "AC-5")
def test_an_unresolved_system_zone_comes_after_the_date_line(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", _raising(LookupError("no key")))
    monkeypatch.setattr(cli_main, "build_deps", _must_not_be_called)

    code = cli_main.main(["--start", "x", "--end", "2026-01-31"])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, f"{START_FORMAT}\n{ZONE_ERROR}\n", "")


@pytest.mark.req("AC-4")
def test_the_system_zone_is_not_looked_up_when_tz_is_given(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", _must_not_be_called)
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    assert cli_main.main(RANGE_ARGS) == 0


@pytest.mark.req("AC-3")
@pytest.mark.parametrize(
    ("end", "warned"),
    [
        pytest.param("2026-02-14", False, id="yesterday"),
        pytest.param("2026-02-15", False, id="today"),
        pytest.param("2026-02-16", True, id="tomorrow"),
        pytest.param("9999-12-30", True, id="the-ceiling"),
    ],
)
def test_a_future_end_date_warns_and_the_run_goes_on(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    end: str,
    warned: bool,
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main(["--start", "2026-01-01", "--end", end, "--tz", "Asia/Kolkata"])

    captured = capsys.readouterr()
    assert (code, captured.out) == (0, "Messages in range: 3\n")
    assert captured.err == (FUTURE_END + "\n" if warned else "")


@pytest.mark.req("AC-3")
def test_today_is_the_day_in_the_chosen_zone_not_in_utc(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    # 12:00 UTC on 2026-02-15 is already 2026-02-16 in UTC+14, so that end date is today there.
    code = cli_main.main(
        ["--start", "2026-01-01", "--end", "2026-02-16", "--tz", "Pacific/Kiritimati"]
    )

    captured = capsys.readouterr()
    assert (code, captured.err) == (0, "")


@pytest.mark.req("AC-3")
def test_a_future_end_date_in_real_mode_warns_and_then_ends_in_the_sign_in_line(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = cli_main.main(["--start", "2026-01-01", "--end", "2026-03-01", "--tz", "UTC"])

    assert (code, capsys.readouterr().err) == (
        3,
        FUTURE_END + "\n" + messages.SIGN_IN_UNAVAILABLE_LINE + "\n",
    )


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
    monkeypatch.setattr(cli_main, "build_deps", _must_not_be_called)
    monkeypatch.setattr(cli_main.runner, "run", _must_not_be_called)

    code = cli_main.main(argv)

    captured = capsys.readouterr()
    assert (code, captured.out) == (2, "")
    assert "unrecognized arguments" in captured.err  # argparse's own wording (issue #23)


@pytest.mark.req("AC-6")
def test_the_full_flag_names_still_work(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    assert cli_main.main(RANGE_ARGS) == 0
    assert capsys.readouterr().out == MESSAGES_IN_RANGE_LINE


@pytest.mark.req("AC-6")
def test_invalid_input_logs_only_the_fixed_lines_and_sets_up_no_log_handler(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(cli_main, "build_deps", _must_not_be_called)
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


# AC-9: every zone, at the floor and at the ceiling, on the fake mailbox. The same sweep reaches
# the real gateway's query in tests/integration/test_gateway_httpmock.py.
@pytest.mark.req("AC-9")
def test_every_zone_runs_the_floor_and_the_ceiling_date_to_a_normal_result(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))
    zones = sorted(available_timezones())
    problems: list[str] = []

    for zone in zones:
        for day, warned in (("1970-01-02", False), ("9999-12-30", True)):
            code = cli_main.main(["--start", day, "--end", day, "--tz", zone])
            captured = capsys.readouterr()
            expected_err = FUTURE_END + "\n" if warned else ""
            if (code, captured.out, captured.err) != (0, "Messages in range: 0\n", expected_err):
                problems.append(f"{zone} {day}: {code} {captured.out!r} {captured.err!r}")

    assert len(zones) > 400
    assert problems == []


def test_the_usage_text_lists_the_three_options(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli_main.main(["--help"]) == 0

    out = capsys.readouterr().out
    assert all(flag in out for flag in ("--start", "--end", "--tz"))


def test_an_unknown_flag_is_still_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli_main.main([*RANGE_ARGS, "--no-such-flag"]) == 2
    capsys.readouterr()
