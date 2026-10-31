"""Helpers and expected lines for the PGD-16 end-to-end tests of invalid input.

The expected lines are literals from the story. Every child runs the real command line under
the socket guard, on a mailbox of four messages or in real mode (no hook variable).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tests.fakes.fake_gmail import FakeGmail
from tests.fakes.fake_gmail_json import dump_fake_gmail_to_json_file
from tests.fixtures.builders import MessageBuilder, build_messages
from tests.support import sentinels
from tests.support.subprocess_env import run_guarded
from tests.support.workspace import Workspace, hook_env

START_FORMAT = "error: --start: Enter the date as YYYY-MM-DD, for example 2026-01-31."

END_FORMAT = "error: --end: Enter the date as YYYY-MM-DD, for example 2026-01-31."

START_BOUNDS = "error: --start: Enter a date from 1970-01-02 to 9999-12-30."

END_BOUNDS = "error: --end: Enter a date from 1970-01-02 to 9999-12-30."

ZONE_ERROR = "error: --tz: Unknown time zone. Use an IANA name such as Asia/Kolkata."

REVERSED = (
    "error: Start date must be on or before the end date. (--start 2026-03-31 --end 2026-01-01)"
)

FUTURE_END = "warning: End date is in the future. Only mail received so far is included."

SIGN_IN_LINE = "error: Gmail sign-in is not available in this build yet."

COUNT_FOUR = "Messages in range: 4\n"


def four_message_mailbox(path: Path) -> Path:
    """Four messages in the range of every AC-9 row: noon UTC on the 10th of February..May 2026."""
    builders = [
        MessageBuilder(f"m{month}").received(f"2026-0{month}-10T12:00:00", "UTC")
        for month in (2, 3, 4, 5)
    ]
    dump_fake_gmail_to_json_file(
        FakeGmail(build_messages(builder.pdf("A.pdf") for builder in builders)), path
    )
    return path


def lines(*parts: str) -> str:
    return "".join(f"{part}\n" for part in parts)


def run_cli(
    workspace: Workspace, argv: list[str], *, hook: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run ``python -m gmail_pdf`` on the four-message mailbox, or in real mode."""
    env = hook_env(four_message_mailbox(workspace.mailbox_path())) if hook else None
    return run_guarded([sys.executable, "-m", "gmail_pdf", *argv], workspace.cwd, env)


def assert_rejected(
    result: subprocess.CompletedProcess[str], workspace: Workspace, *expected: str
) -> None:
    """Exit 2, exactly these stderr lines, nothing on stdout, nothing created, nothing leaked."""
    assert (result.returncode, result.stderr, result.stdout) == (2, lines(*expected), "")
    assert SIGN_IN_LINE not in result.stderr  # build_deps was not reached
    assert "Traceback" not in result.stderr
    assert sentinels.leaked(result.stdout + result.stderr) == []
    assert workspace.created_files() == []
