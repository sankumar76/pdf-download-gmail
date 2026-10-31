"""PGD-16 end to end: bad input is rejected before anything is sent to Google (child processes).

Every child runs under the socket guard in an empty working directory, so "no Google call" and
"no file or folder is created" are checked, not assumed. The expected lines are literals from
the story. Real mode means neither ``GMAIL_PDF_TESTING`` nor ``GMAIL_PDF_TEST_FAKE_MAILBOX`` is
set: there ``build_deps`` would end in exit 3 (sign-in not available), so an exit 2 proves the
validation ran first.

A child cannot be given a frozen clock, so rows that must not depend on the machine's date use
dates that no sane date can reach (9999-12-30 is always in the future, 2026-01-31 is long past),
or accept either outcome of the future-end warning where the story's row does not decide it.

The helpers and the expected lines are in ``tests/support/invalid_input_cli.py``; the AC-9 rows
(floor and ceiling dates) are in ``tests/e2e/test_invalid_bounds.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from gmail_pdf.domain import messages
from tests.support import sentinels
from tests.support.invalid_input_cli import (
    COUNT_FOUR,
    END_FORMAT,
    FUTURE_END,
    REVERSED,
    SIGN_IN_LINE,
    START_FORMAT,
    ZONE_ERROR,
    assert_rejected,
    four_message_mailbox,
    lines,
    run_cli,
)
from tests.support.mailboxes import RANGE_ARGS
from tests.support.subprocess_env import run_guarded
from tests.support.workspace import Workspace, hook_env

pytestmark = pytest.mark.req("FR-015", "NFR-024")


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    return Workspace(tmp_path)


MODES = [pytest.param(True, id="test-hook"), pytest.param(False, id="real-mode")]

# ----------------------------------------------------------------------------------- AC-1
MALFORMED = [
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
@pytest.mark.parametrize("hook", MODES)
@pytest.mark.parametrize("text", MALFORMED)
def test_a_malformed_start_date_gets_the_format_line_and_nothing_runs(
    workspace: Workspace, text: str, hook: bool
) -> None:
    result = run_cli(workspace, ["--start", text, "--end", "2026-01-31", "--tz", "UTC"], hook=hook)

    assert_rejected(result, workspace, START_FORMAT)


@pytest.mark.req("AC-1", "AC-6")
@pytest.mark.parametrize("text", MALFORMED)
def test_a_malformed_end_date_gets_the_format_line_and_nothing_runs(
    workspace: Workspace, text: str
) -> None:
    result = run_cli(workspace, ["--start", "2026-01-01", "--end", text, "--tz", "UTC"])

    assert_rejected(result, workspace, END_FORMAT)


@pytest.mark.req("AC-1")
@pytest.mark.parametrize("hook", MODES)
@pytest.mark.parametrize(
    ("argv", "line"),
    [
        pytest.param(["--start", "2026-01-01", "--tz", "UTC"], END_FORMAT, id="only-start"),
        pytest.param(["--end", "2026-01-31", "--tz", "UTC"], START_FORMAT, id="only-end"),
    ],
)
def test_only_one_date_reports_the_missing_one_with_the_date_sentence(
    workspace: Workspace, argv: list[str], line: str, hook: bool
) -> None:
    result = run_cli(workspace, argv, hook=hook)

    assert_rejected(result, workspace, line)


@pytest.mark.req("AC-1")
@pytest.mark.parametrize("extra", [[], ["--tz", "Mars/Olympus"]], ids=["no-options", "only-tz"])
def test_with_neither_date_the_usage_text_and_exit_zero_stay(
    workspace: Workspace, extra: list[str]
) -> None:
    result = run_cli(workspace, extra)

    assert (result.returncode, result.stderr) == (0, "")
    assert result.stdout.startswith("usage: gmail-pdf")
    assert workspace.created_files() == []


# ----------------------------------------------------------------------------------- AC-2
@pytest.mark.req("AC-2", "AC-6")
@pytest.mark.parametrize("hook", MODES)
def test_a_reversed_range_exits_two_in_both_modes_never_three(
    workspace: Workspace, hook: bool
) -> None:
    result = run_cli(
        workspace, ["--start", "2026-03-31", "--end", "2026-01-01", "--tz", "UTC"], hook=hook
    )

    assert_rejected(result, workspace, REVERSED)


@pytest.mark.req("AC-2")
def test_start_equal_to_end_is_a_valid_range(workspace: Workspace) -> None:
    result = run_cli(workspace, ["--start", "2026-03-10", "--end", "2026-03-10", "--tz", "UTC"])

    assert (result.returncode, result.stdout, result.stderr) == (0, "Messages in range: 1\n", "")


# ----------------------------------------------------------------------------------- AC-3
@pytest.mark.req("AC-3")
def test_a_future_end_date_warns_on_stderr_and_the_run_goes_on(workspace: Workspace) -> None:
    result = run_cli(workspace, ["--start", "2026-01-01", "--end", "9999-12-30", "--tz", "UTC"])

    assert (result.returncode, result.stdout, result.stderr) == (0, COUNT_FOUR, lines(FUTURE_END))


@pytest.mark.req("AC-3")
def test_a_past_end_date_gives_no_warning(workspace: Workspace) -> None:
    result = run_cli(workspace, RANGE_ARGS)

    assert (result.returncode, result.stderr) == (0, "")


# ----------------------------------------------------------------------------------- AC-4
UNKNOWN_ZONES = [
    pytest.param("Mars/Olympus", id="unknown"),
    pytest.param("IST", id="abbreviation"),
    pytest.param("", id="empty"),
    pytest.param("Asia/Kolkata ", id="trailing-space"),
    pytest.param("Asia\\Kolkata", id="backslash"),
    pytest.param("utc", id="lower-case-utc"),
    pytest.param("asia/kolkata", id="lower-case-kolkata"),
]


@pytest.mark.req("AC-4", "AC-6")
@pytest.mark.parametrize("hook", MODES)
@pytest.mark.parametrize("zone", UNKNOWN_ZONES)
def test_a_zone_outside_the_iana_set_exits_two_in_both_modes_never_three(
    workspace: Workspace, zone: str, hook: bool
) -> None:
    result = run_cli(
        workspace, ["--start", "2026-01-01", "--end", "2026-01-31", "--tz", zone], hook=hook
    )

    assert_rejected(result, workspace, ZONE_ERROR)


@pytest.mark.req("AC-4")
@pytest.mark.parametrize("zone", ["UTC", "Asia/Kolkata"])
@pytest.mark.parametrize(
    ("hook", "code", "stderr"),
    [
        pytest.param(True, 0, "", id="test-hook"),
        pytest.param(False, 3, lines(SIGN_IN_LINE), id="real-mode"),
    ],
)
def test_a_zone_in_the_iana_set_is_accepted_and_the_run_goes_on(
    workspace: Workspace, zone: str, hook: bool, code: int, stderr: str
) -> None:
    result = run_cli(
        workspace, ["--start", "2026-03-10", "--end", "2026-03-10", "--tz", zone], hook=hook
    )

    assert (result.returncode, result.stderr) == (code, stderr)


# ----------------------------------------------------------------------------------- AC-5
@pytest.mark.req("AC-5")
@pytest.mark.parametrize("hook", MODES)
@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        pytest.param(
            ["--start", "2026-1-5", "--end", "nope", "--tz", "Mars/Olympus"],
            (START_FORMAT, END_FORMAT, ZONE_ERROR),
            id="start-end-zone",
        ),
        pytest.param(
            ["--start", "2026-03-31", "--end", "2026-01-01", "--tz", "Mars/Olympus"],
            (REVERSED, ZONE_ERROR),
            id="range-zone",
        ),
    ],
)
def test_several_errors_print_one_per_line_in_the_order_start_end_range_zone(
    workspace: Workspace, argv: list[str], expected: tuple[str, ...], hook: bool
) -> None:
    result = run_cli(workspace, argv, hook=hook)

    assert_rejected(result, workspace, *expected)


# ----------------------------------------------------------------------------------- AC-6
@pytest.mark.req("AC-6")
@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["--sta", "2026-01-01", "--end", "2026-01-31", "--tz", "UTC"], id="--sta"),
        pytest.param(["--start", "2026-01-01", "--en", "2026-01-31", "--tz", "UTC"], id="--en"),
        pytest.param(["--start", "2026-01-01", "--end", "2026-01-31", "--t", "UTC"], id="--t"),
    ],
)
@pytest.mark.parametrize("hook", MODES)
def test_an_abbreviated_flag_is_an_unknown_flag_exit_two_and_nothing_runs(
    workspace: Workspace, argv: list[str], hook: bool
) -> None:
    result = run_cli(workspace, argv, hook=hook)

    assert (result.returncode, result.stdout) == (2, "")
    assert "unrecognized arguments" in result.stderr  # argparse's own wording (issue #23)
    assert SIGN_IN_LINE not in result.stderr
    assert "Traceback" not in result.stderr
    assert workspace.created_files() == []


@pytest.mark.req("AC-6")
def test_the_full_flag_names_still_work(workspace: Workspace) -> None:
    result = run_cli(workspace, ["--start", "2026-03-10", "--end", "2026-03-10", "--tz", "UTC"])

    assert (result.returncode, result.stdout) == (0, "Messages in range: 1\n")


@pytest.mark.req("AC-6")
def test_a_rejection_comes_before_the_hook_file_is_read_and_creates_nothing(
    workspace: Workspace,
) -> None:
    # The hook variable names a file that does not exist. Reached, ``build_deps`` would end in
    # exit 1 with the "could not be read" line; a rejection must come first.
    missing = workspace.fixtures / "absent.json"

    result = run_guarded(
        [
            sys.executable,
            "-m",
            "gmail_pdf",
            "--start",
            "2026-1-1",
            "--end",
            "2026-01-31",
            "--tz",
            "UTC",
        ],
        workspace.cwd,
        hook_env(missing),
    )

    assert_rejected(result, workspace, START_FORMAT)
    assert messages.FAKE_MAILBOX_UNREADABLE_LINE not in result.stderr
    assert not missing.exists()


@pytest.mark.req("AC-6")
def test_a_rejection_comes_before_the_refused_hook_line(workspace: Workspace) -> None:
    # The hook variable is set without ``GMAIL_PDF_TESTING=1``. Reached, ``build_deps`` would
    # refuse it with exit 1; invalid input must be reported first, with exit 2.
    mailbox = four_message_mailbox(workspace.mailbox_path())

    result = run_guarded(
        [sys.executable, "-m", "gmail_pdf", "--start", "2026-1-1", "--end", "2026-01-31"]
        + ["--tz", "UTC"],
        workspace.cwd,
        hook_env(mailbox, testing=None),
    )

    assert_rejected(result, workspace, START_FORMAT)
    assert messages.FAKE_MAILBOX_HOOK_REFUSED_LINE not in result.stderr


# ----------------------------------------------------------------------------------- AC-8
@pytest.mark.req("AC-8")
@pytest.mark.parametrize("hook", MODES)
def test_a_secret_typed_as_the_start_date_appears_on_no_surface(
    workspace: Workspace, hook: bool
) -> None:
    result = run_cli(
        workspace,
        ["--start", sentinels.CLIENT_SECRET, "--end", "2026-01-31", "--tz", "UTC"],
        hook=hook,
    )

    assert_rejected(result, workspace, START_FORMAT)
    assert sentinels.CLIENT_SECRET not in result.stdout + result.stderr
