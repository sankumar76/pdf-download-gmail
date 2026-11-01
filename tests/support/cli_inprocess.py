"""Helpers for the tests that call ``cli.main.main`` in this process."""

from __future__ import annotations

from pathlib import Path
from typing import NoReturn

import pytest

from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING


def use_hook(monkeypatch: pytest.MonkeyPatch, path: Path, testing: str | None = "1") -> None:
    """Point the test hook at ``path``; ``testing`` None leaves ``GMAIL_PDF_TESTING`` unset."""
    monkeypatch.setenv(ENV_FAKE_MAILBOX, str(path))
    if testing is not None:
        monkeypatch.setenv(ENV_TESTING, testing)


def must_not_be_called(*_args: object) -> NoReturn:
    """A stub that fails the test when reached: ``build_deps``, the run or a zone lookup."""
    raise AssertionError("this call must not be reached in this test")
