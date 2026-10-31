"""A working directory and a hook environment for the command-line tests that start a child.

Every child runs under the socket guard (``run_guarded``) in an empty working directory, so "no
network call" and "no file or folder is created" are checked, not assumed. The hook is the one of
test-strategy section 2: ``GMAIL_PDF_TESTING=1`` plus ``GMAIL_PDF_TEST_FAKE_MAILBOX``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from tests.support import sentinels
from tests.support.mailboxes import RANGE_ARGS
from tests.support.subprocess_env import run_guarded

# A sentinel in the mailbox file name: it must appear on no surface.
PATH_SENTINEL = sentinels.CLIENT_SECRET


class Workspace:
    """An empty working directory for the child, and a separate directory for fixture files."""

    def __init__(self, tmp_path: Path) -> None:
        self.cwd = tmp_path / "cwd"
        self.fixtures = tmp_path / "fixtures"
        self.cwd.mkdir()
        self.fixtures.mkdir()

    def mailbox_path(self) -> Path:
        return self.fixtures / f"mailbox-{PATH_SENTINEL}.json"

    def run(
        self, extra_env: dict[str, str] | None = None, args: list[str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-m", "gmail_pdf", *(RANGE_ARGS if args is None else args)]
        return run_guarded(command, self.cwd, extra_env)

    def created_files(self) -> list[str]:
        return sorted(str(p) for p in self.cwd.rglob("*"))


def hook_env(path: Path, *, testing: str | None = "1") -> dict[str, str]:
    """The environment that points the child at a fake mailbox file (``testing`` None: unset)."""
    env = {ENV_FAKE_MAILBOX: str(path)}
    if testing is not None:
        env[ENV_TESTING] = testing
    return env
