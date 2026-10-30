"""Environment for guarded child processes (no network, deterministic output)."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

SUPPORT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SUPPORT_DIR.parent.parent


def guarded_env(extra: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return an environment whose Python children block non-loopback sockets.

    The repo root is also on ``PYTHONPATH`` so ``python -m gmail_pdf`` works from any cwd.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(SUPPORT_DIR), str(REPO_ROOT)])
    env["PYTHONUTF8"] = "1"
    # A child's stderr is compared byte for byte; inherited interpreter options (warnings,
    # dev mode, startup script) must not add lines to it.
    for name in ("PYTHONWARNINGS", "PYTHONDEVMODE", "PYTHONSTARTUP"):
        env.pop(name, None)
    env.pop("GMAIL_PDF_TESTING", None)
    env.pop("GMAIL_PDF_TEST_FAKE_MAILBOX", None)
    if extra:
        env.update(extra)
    return env


SUBPROCESS_TIMEOUT_S = 60


def run_guarded(
    args: Sequence[str], cwd: Path, extra_env: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Run a child process with the egress guard active and capture its text output."""
    return subprocess.run(
        list(args),
        cwd=cwd,
        env=guarded_env(extra_env),
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT_S,
        check=False,
    )
