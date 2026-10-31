"""Composition root: wires adapters into ``Deps`` for the CLI and the GUI (one place).

Test-only seam (test-strategy section 2): setting ``GMAIL_PDF_TEST_FAKE_MAILBOX`` to a JSON
file makes ``build_deps`` return the in-memory ``FakeGmail`` loaded from it. The hook is
inert unless ``GMAIL_PDF_TESTING=1`` is also set; with the file variable alone it is refused.
"""

from __future__ import annotations

import importlib
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from gmail_pdf.app.ports import GmailPort
from gmail_pdf.domain.errors import (
    AdapterUnavailableError,
    FakeMailboxHookRefusedError,
    FakeMailboxNotImportableError,
    FakeMailboxUnavailableError,
)

ENV_TESTING = "GMAIL_PDF_TESTING"
ENV_FAKE_MAILBOX = "GMAIL_PDF_TEST_FAKE_MAILBOX"

# The fake lives with the tests, never in the shipped package; it is imported lazily so a
# normal run (and the wheel) never needs it.
_FAKE_MODULE = "tests.fakes.fake_gmail_json"
_FAKE_LOADER = "load_fake_gmail_from_json_file"
# Only these names mean "the tests package is not importable"; any other missing module is a
# real defect inside the fake and must surface unchanged.
_ABSENT_TEST_PACKAGES = frozenset({"tests", "tests.fakes"})


@dataclass(frozen=True, slots=True)
class Deps:
    """Port implementations handed to the application layer."""

    gmail: GmailPort


def _load_fake_mailbox(path: Path) -> GmailPort:
    """Load ``FakeGmail`` from a JSON file (test-only).

    Raises:
        FakeMailboxNotImportableError: ``tests/`` is not importable.
        FakeMailboxUnavailableError: the file cannot be read or parsed. The message never
            contains the path. Both are ``AdapterUnavailableError`` subclasses.
    """
    try:
        module = importlib.import_module(_FAKE_MODULE)
    except ModuleNotFoundError as exc:
        if exc.name not in _ABSENT_TEST_PACKAGES | {_FAKE_MODULE}:
            raise
        raise FakeMailboxNotImportableError(
            "The fake mailbox is only available from a source checkout (tests/ not importable)."
        ) from exc
    loader = getattr(module, _FAKE_LOADER)
    try:
        return cast(GmailPort, loader(path))
    except (OSError, ValueError, RecursionError) as exc:  # JSONDecodeError is a ValueError
        raise FakeMailboxUnavailableError(
            f"The fake mailbox file could not be read; check {ENV_FAKE_MAILBOX}."
        ) from exc


def build_deps(env: Mapping[str, str] | None = None) -> Deps:
    """Build the port implementations for this process.

    Args:
        env: Environment to read; ``os.environ`` when ``None``.

    Returns:
        The wired ``Deps``.

    Raises:
        FakeMailboxHookRefusedError: ``GMAIL_PDF_TEST_FAKE_MAILBOX`` is set but
            ``GMAIL_PDF_TESTING`` is not ``1``.
        AdapterUnavailableError: no Gmail adapter is wired yet (real gateway: later story).
        FakeMailboxUnavailableError: the fake mailbox file is unreadable or malformed.
        FakeMailboxNotImportableError: ``tests/`` is not importable.
    """
    environment = os.environ if env is None else env
    mailbox_file = environment.get(ENV_FAKE_MAILBOX)
    if mailbox_file:
        if environment.get(ENV_TESTING) != "1":
            raise FakeMailboxHookRefusedError(
                f"{ENV_FAKE_MAILBOX} is a test-only setting and needs {ENV_TESTING}=1."
            )
        return Deps(gmail=_load_fake_mailbox(Path(mailbox_file)))
    raise AdapterUnavailableError("The Gmail adapter is not available in this build yet.")
