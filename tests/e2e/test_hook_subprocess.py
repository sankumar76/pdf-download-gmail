"""Child-process checks: the egress guard and the fake-mailbox hook cross a process boundary."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from tests.fakes.fake_gmail import FakeGmail
from tests.fakes.fake_gmail_json import dump_fake_gmail_to_json_file
from tests.fixtures.canonical import rd_example_table
from tests.support.socket_guard import DOCUMENTATION_ADDRESS
from tests.support.subprocess_env import REPO_ROOT, run_guarded


@pytest.mark.req("NFR-014", "AC-8")
def test_guard_is_active_in_a_guarded_child_process(tmp_path: Path) -> None:
    code = (
        "import socket\n"
        "try:\n"
        f"    socket.create_connection(('{DOCUMENTATION_ADDRESS}', 443), timeout=1)\n"
        "except RuntimeError as exc:\n"
        "    print(type(exc).__name__)\n"
    )

    result = run_guarded([sys.executable, "-c", code], tmp_path)

    assert result.stdout.strip() == "NetworkAccessError", result.stderr


@pytest.mark.req("NFR-014", "AC-9")
def test_fake_mailbox_hook_builds_deps_in_a_child_process(tmp_path: Path) -> None:
    """The pattern later e2e stories use: a child process builds Deps from the environment."""
    mailbox = tmp_path / "mailbox.json"
    dump_fake_gmail_to_json_file(FakeGmail([row.message for row in rd_example_table()]), mailbox)
    code = (
        "from gmail_pdf.bootstrap import build_deps\nprint(len(build_deps().gmail.message_ids))\n"
    )

    result = run_guarded(
        [sys.executable, "-c", code],
        REPO_ROOT,
        {ENV_FAKE_MAILBOX: str(mailbox), ENV_TESTING: "1"},
    )

    assert result.stdout.strip() == "6", result.stderr
