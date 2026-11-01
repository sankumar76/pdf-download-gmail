"""PGD-16 AC-9 end to end: the floor and the ceiling date, as real children (DEF-007).

The rows of the story's Testing Notes, run on a mailbox of four messages under the socket guard
in an empty working directory. The other PGD-16 rows are in ``tests/e2e/test_invalid_input.py``;
the helpers and the expected lines are in ``tests/support/invalid_input_cli.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.support.invalid_input_cli import (
    COUNT_FOUR,
    END_BOUNDS,
    FUTURE_END,
    START_BOUNDS,
    ZONE_ERROR,
    assert_rejected,
    lines,
    run_cli,
)
from tests.support.mailboxes import RANGE_ARGS, write_edge_mailbox
from tests.support.subprocess_env import run_guarded
from tests.support.workspace import Workspace, hook_env

pytestmark = pytest.mark.req("FR-015", "NFR-024")


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    return Workspace(tmp_path)


# ----------------------------------------------------------------------------------- AC-9
# The rows of the story's Testing Notes, run as real children on a mailbox of four messages.
ZONES_EAST = ["UTC", "Pacific/Kiritimati", "Pacific/Apia", "Etc/GMT-14"]


@pytest.mark.req("AC-9", "DEF-007")
def test_the_floor_day_alone_is_a_normal_empty_result(workspace: Workspace) -> None:
    result = run_cli(workspace, ["--start", "1970-01-02", "--end", "1970-01-02", "--tz", "UTC"])

    assert (result.returncode, result.stdout, result.stderr) == (
        0,
        "No PDFs found\n0 PDFs found.\n",
        "",
    )


@pytest.mark.req("AC-9", "DEF-007")
@pytest.mark.parametrize("zone", ZONES_EAST)
def test_from_the_floor_to_the_end_of_2026_finds_the_four_messages(
    workspace: Workspace, zone: str
) -> None:
    result = run_cli(workspace, ["--start", "1970-01-02", "--end", "2026-12-31", "--tz", zone])

    assert (result.returncode, result.stdout) == (0, COUNT_FOUR)
    assert result.stderr in ("", lines(FUTURE_END))  # 2026-12-31 may or may not be past


@pytest.mark.req("AC-9", "DEF-007")
def test_the_year_2000_to_the_end_of_2026_finds_the_four_messages(workspace: Workspace) -> None:
    result = run_cli(workspace, ["--start", "2000-01-01", "--end", "2026-12-31", "--tz", "UTC"])

    assert (result.returncode, result.stdout) == (0, COUNT_FOUR)
    assert result.stderr in ("", lines(FUTURE_END))


@pytest.mark.req("AC-9", "AC-3", "DEF-007")
@pytest.mark.parametrize("zone", ["UTC", "Etc/GMT-14", "Etc/GMT+12"])
def test_to_the_ceiling_date_gives_the_future_warning_and_a_normal_result(
    workspace: Workspace, zone: str
) -> None:
    result = run_cli(workspace, ["--start", "2026-01-01", "--end", "9999-12-30", "--tz", zone])

    assert (result.returncode, result.stdout, result.stderr) == (0, COUNT_FOUR, lines(FUTURE_END))


@pytest.mark.req("AC-9", "DEF-007")
@pytest.mark.parametrize("day", ["1970-01-01", "1969-12-31"])
def test_a_single_day_below_the_floor_gets_a_start_line_and_an_end_line(
    workspace: Workspace, day: str
) -> None:
    result = run_cli(workspace, ["--start", day, "--end", day, "--tz", "UTC"])

    assert_rejected(result, workspace, START_BOUNDS, END_BOUNDS)


BELOW_THE_FLOOR = [
    pytest.param("1970-01-01", "UTC", id="epoch-day-utc"),
    pytest.param("1970-01-01", "Asia/Kolkata", id="epoch-day-kolkata"),
    pytest.param("1970-01-01", "America/New_York", id="epoch-day-new-york-was-exit-0"),
    pytest.param("1960-01-01", "UTC", id="1960"),
    pytest.param("1900-01-01", "Asia/Kolkata", id="1900-kolkata"),
    pytest.param("0001-01-01", "UTC", id="year-one"),
]


@pytest.mark.req("AC-9", "DEF-007")
@pytest.mark.parametrize(("start", "zone"), BELOW_THE_FLOOR)
def test_a_start_below_the_floor_is_one_start_line_though_the_range_holds_four_messages(
    workspace: Workspace, start: str, zone: str
) -> None:
    result = run_cli(workspace, ["--start", start, "--end", "2026-12-31", "--tz", zone])

    assert_rejected(result, workspace, START_BOUNDS)


@pytest.mark.req("AC-9", "DEF-007")
def test_in_real_mode_a_start_in_1960_is_exit_two_not_three(workspace: Workspace) -> None:
    result = run_cli(
        workspace, ["--start", "1960-01-01", "--end", "2026-12-31", "--tz", "UTC"], hook=False
    )

    assert_rejected(result, workspace, START_BOUNDS)


@pytest.mark.req("AC-9", "DEF-007")
@pytest.mark.parametrize("zone", ["UTC", "Asia/Kolkata", "Etc/GMT+12", "Etc/GMT-14"])
def test_an_end_date_after_the_ceiling_is_one_end_line_in_any_zone(
    workspace: Workspace, zone: str
) -> None:
    result = run_cli(workspace, ["--start", "2026-01-01", "--end", "9999-12-31", "--tz", zone])

    assert_rejected(result, workspace, END_BOUNDS)


@pytest.mark.req("AC-9")
def test_the_last_day_alone_is_rejected_as_start_and_end(workspace: Workspace) -> None:
    result = run_cli(workspace, ["--start", "9999-12-31", "--end", "9999-12-31", "--tz", "UTC"])

    assert_rejected(result, workspace, START_BOUNDS, END_BOUNDS)


@pytest.mark.req("AC-9", "AC-5")
def test_two_dates_below_the_floor_in_reversed_order_get_no_reversed_range_line(
    workspace: Workspace,
) -> None:
    result = run_cli(workspace, ["--start", "1960-01-01", "--end", "1950-01-01", "--tz", "UTC"])

    assert_rejected(result, workspace, START_BOUNDS, END_BOUNDS)


@pytest.mark.req("AC-9", "AC-5")
def test_a_date_below_the_floor_and_an_unknown_zone_get_two_lines(workspace: Workspace) -> None:
    result = run_cli(
        workspace, ["--start", "1970-01-01", "--end", "2026-01-01", "--tz", "Mars/Olympus"]
    )

    assert_rejected(result, workspace, START_BOUNDS, ZONE_ERROR)


@pytest.mark.req("AC-6")
def test_the_edge_mailbox_still_counts_two_for_the_pgd_15_range(workspace: Workspace) -> None:
    """Control: a valid range on the PGD-15 mailbox is untouched by the new checks."""
    path = write_edge_mailbox(workspace.mailbox_path())

    result = run_guarded(
        [sys.executable, "-m", "gmail_pdf", *RANGE_ARGS], workspace.cwd, hook_env(path)
    )

    assert (result.returncode, result.stdout, result.stderr) == (0, "Messages in range: 2\n", "")
