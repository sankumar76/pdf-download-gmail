"""Environment for guarded child processes (no network, deterministic output)."""

from __future__ import annotations

import os
from collections.abc import Mapping
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
    env.pop("GMAIL_PDF_TESTING", None)
    env.pop("GMAIL_PDF_TEST_FAKE_MAILBOX", None)
    if extra:
        env.update(extra)
    return env
