"""PGD-17 AC-1..AC-3 end to end: a range with no matching mail ends normally (child process).

Every child runs under the socket guard in an empty working directory, so "no file or folder is
created" is checked, not assumed. The expected lines are literals from the story. Each mailbox is
run once per module: the tests below read different parts of the same finished run.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest

from tests.support.mailboxes import RANGE_ARGS, write_empty_mailbox, write_outside_mailbox
from tests.support.workspace import Workspace, hook_env

pytestmark = pytest.mark.req("FR-016", "EC-06")

EMPTY_OUTPUT = "No PDFs found\n0 PDFs found.\n"
FUTURE_WARNING = "warning: End date is in the future. Only mail received so far is included.\n"
# 2099 is always in the future, so the row never depends on the machine's date.
FUTURE_END_ARGS = ["--start", "2026-01-01", "--end", "2099-12-31", "--tz", "Asia/Kolkata"]

MAILBOXES: dict[str, Callable[[Path], Path]] = {
    "search-returns-nothing": write_empty_mailbox,
    "every-message-outside-the-range": write_outside_mailbox,
}


@dataclass(frozen=True)
class FinishedRun:
    returncode: int
    stdout: str
    stderr: str
    created: list[str]


def _run(tmp_path_factory: pytest.TempPathFactory, name: str, args: list[str]) -> FinishedRun:
    workspace = Workspace(tmp_path_factory.mktemp(name))
    path = MAILBOXES[name](workspace.mailbox_path())
    result = workspace.run(hook_env(path), args)
    return FinishedRun(result.returncode, result.stdout, result.stderr, workspace.created_files())


@pytest.fixture(scope="module", params=list(MAILBOXES))
def empty_run(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> FinishedRun:
    return _run(tmp_path_factory, request.param, RANGE_ARGS)


@pytest.fixture(scope="module")
def future_end_run(tmp_path_factory: pytest.TempPathFactory) -> FinishedRun:
    return _run(tmp_path_factory, "search-returns-nothing", FUTURE_END_ARGS)


# ------------------------------------------------------------------------------- AC-1, AC-2
@pytest.mark.req("AC-1", "AC-2")
def test_the_first_stdout_line_is_no_pdfs_found(empty_run: FinishedRun) -> None:
    assert empty_run.stdout.splitlines()[0] == "No PDFs found"


@pytest.mark.req("AC-1", "AC-2")
def test_stdout_is_the_two_lines_and_nothing_else(empty_run: FinishedRun) -> None:
    assert empty_run.stdout == EMPTY_OUTPUT


@pytest.mark.req("AC-1", "AC-2")
def test_the_exit_code_is_zero(empty_run: FinishedRun) -> None:
    assert empty_run.returncode == 0, empty_run.stderr


@pytest.mark.req("AC-1", "AC-2")
def test_the_interim_count_line_is_gone_for_an_empty_range(empty_run: FinishedRun) -> None:
    assert "Messages in range" not in empty_run.stdout


# ------------------------------------------------------------------------------------- AC-3
@pytest.mark.req("AC-3")
def test_stderr_is_empty(empty_run: FinishedRun) -> None:
    assert empty_run.stderr == ""


@pytest.mark.req("AC-3")
def test_there_is_no_error_warning_or_trace_line_anywhere(empty_run: FinishedRun) -> None:
    surfaces = empty_run.stdout + empty_run.stderr

    assert ("error:" in surfaces, "warning:" in surfaces, "Traceback" in surfaces) == (
        False,
        False,
        False,
    )


@pytest.mark.req("AC-3")
def test_no_file_or_folder_is_created(empty_run: FinishedRun) -> None:
    assert empty_run.created == []


# ------------------------------------------------------------- empty range with a future end
@pytest.mark.req("AC-1", "AC-3")
def test_a_future_end_warns_on_stderr_and_still_ends_normally(future_end_run: FinishedRun) -> None:
    assert (future_end_run.returncode, future_end_run.stdout, future_end_run.stderr) == (
        0,
        EMPTY_OUTPUT,
        FUTURE_WARNING,
    )


@pytest.mark.req("AC-3")
def test_a_future_end_creates_nothing(future_end_run: FinishedRun) -> None:
    assert future_end_run.created == []
