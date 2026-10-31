"""PGD-15 AC-5, AC-6 and the usage errors, through ``cli.main.main`` in this process.

The subprocess versions of AC-5 and AC-6 are in ``tests/e2e/test_select_range.py``. Here the
exit codes, the single stderr line, the log records and the "no fall-through" rule are checked
with the real code and a monkeypatched environment.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from gmail_pdf.cli import main as cli_main
from gmail_pdf.domain import messages
from tests.support import sentinels
from tests.support.mailboxes import MESSAGES_IN_RANGE_LINE, RANGE_ARGS, write_edge_mailbox

pytestmark = pytest.mark.req("FR-008", "FR-012")


@pytest.fixture(autouse=True)
def _no_hook_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every test in real mode, whatever the developer's shell holds."""
    monkeypatch.delenv(ENV_FAKE_MAILBOX, raising=False)
    monkeypatch.delenv(ENV_TESTING, raising=False)


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
    from gmail_pdf.infra import tz as tz_module

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
    monkeypatch.setattr(cli_main.runner, "run", _must_not_run)
    use_hook(
        monkeypatch,
        tmp_path / "absent.json" if case == "unusable" else write_edge_mailbox(tmp_path / "m.json"),
        "1" if case == "unusable" else None,
    )

    code = cli_main.main(RANGE_ARGS)

    assert (code, len(builds)) == (1, 1)


def _must_not_run(*_args: object) -> object:
    raise AssertionError("the run must not start after a hook failure")


# ------------------------------------------------------------------------- usage errors
@pytest.mark.parametrize(
    ("argv", "line"),
    [
        pytest.param(
            ["--start", "2026-01-01"],
            "error: --start and --end must be given together.",
            id="only-start",
        ),
        pytest.param(
            ["--end", "2026-01-31"],
            "error: --start and --end must be given together.",
            id="only-end",
        ),
        pytest.param(
            ["--start", "2026-1-1", "--end", "2026-01-31"],
            "error: --start must be a date written as YYYY-MM-DD.",
            id="bad-start",
        ),
        pytest.param(
            ["--start", "2026-01-01", "--end", "31/01/2026"],
            "error: --end must be a date written as YYYY-MM-DD.",
            id="bad-end",
        ),
    ],
)
def test_bad_dates_exit_two_before_any_adapter_work(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, argv: list[str], line: str
) -> None:
    monkeypatch.setattr(cli_main, "build_deps", _must_not_run)

    code = cli_main.main(argv)

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, line + "\n", "")


@pytest.mark.parametrize(
    ("argv", "line"),
    [
        pytest.param(
            ["--start", "2026-01-01", "--end", "2026-01-31", "--tz", "Mars/Olympus_Mons"],
            "error: " + messages.ZONE_UNKNOWN,
            id="unknown-zone",
        ),
        pytest.param(
            ["--start", "2026-02-01", "--end", "2026-01-31", "--tz", "UTC"],
            "error: " + messages.END_BEFORE_START,
            id="end-before-start",
        ),
    ],
)
def test_a_bad_zone_or_range_order_exits_two(
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


def test_a_bad_value_is_never_echoed(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))
    secret_zone = f"Zone/{sentinels.CLIENT_SECRET}"

    cli_main.main(["--start", "2026-01-01", "--end", "2026-01-31", "--tz", secret_zone])
    cli_main.main(["--start", sentinels.REFRESH_TOKEN, "--end", "2026-01-31"])

    captured = capsys.readouterr()
    assert sentinels.leaked(captured.err + captured.out) == []


def test_the_usage_text_lists_the_three_options(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli_main.main(["--help"]) == 0

    out = capsys.readouterr().out
    assert all(flag in out for flag in ("--start", "--end", "--tz"))


def test_an_unknown_flag_is_still_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli_main.main([*RANGE_ARGS, "--no-such-flag"]) == 2
    capsys.readouterr()
