"""PGD-15 AC-5, AC-6 and the success paths of PGD-16 through ``cli.main.main`` in this process.

The PGD-16 rejection tests are in ``tests/unit/test_cli_invalid_input.py``. The subprocess
versions of both are in ``tests/e2e/test_select_range.py`` and ``tests/e2e/test_invalid_input.py``.
Here the exit codes, the stderr lines, the log records, the order "validate, then ``build_deps``"
and the "no fall-through" rule are checked with the real code and a monkeypatched environment.
"Today" is a clock frozen at 2026-02-15 12:00 UTC.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import available_timezones

import pytest

from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from gmail_pdf.cli import main as cli_main
from gmail_pdf.domain import messages
from gmail_pdf.domain.models import RunResult, RunSummary
from gmail_pdf.infra import tz as tz_module
from tests.fakes.fake_time import FixedInstantClock
from tests.support import sentinels
from tests.support.cli_inprocess import must_not_be_called, use_hook
from tests.support.mailboxes import MESSAGES_IN_RANGE_LINE, RANGE_ARGS, write_edge_mailbox

pytestmark = pytest.mark.req("FR-008", "FR-012")

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
    monkeypatch.setattr(cli_main.runner, "run", must_not_be_called)
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


@pytest.mark.req("AC-4")
def test_the_system_zone_is_not_looked_up_when_tz_is_given(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", must_not_be_called)
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


@pytest.mark.req("AC-6")
def test_the_full_flag_names_still_work(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    assert cli_main.main(RANGE_ARGS) == 0
    assert capsys.readouterr().out == MESSAGES_IN_RANGE_LINE


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
            expected_out = "No PDFs found\n0 PDFs found.\n"
            if (code, captured.out, captured.err) != (0, expected_out, expected_err):
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
