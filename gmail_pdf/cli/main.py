"""Command-line entry points.

``main(argv)`` is the single entry used by the ``gmail-pdf`` console script, by
``python -m gmail_pdf`` and by the repo-root ``gmail_pdf_downloader.py`` shim (ADR-005).

Parsing happens before any path resolution, credential read, logging set-up or network call
(PD-16), so ``--help`` is always safe to run. Without ``--start`` and ``--end`` the usage text is
shown. With them, the run selects the messages in the inclusive date range (PGD-15); the full
flag table arrives with STORY-07.01.

Redaction comes first (PGD-13 AC-7): ``main`` installs the logging caps and the excepthooks
before the parser is built, so no log record or uncaught exception exists without them.
``argparse`` usage errors are not redacted yet (issue #23). A failure that escapes the run
prints one fixed line and exits 1; Ctrl+C prints ``Run cancelled`` and also exits 1
(decision D-21).

Expected failures are handled before that last line of defence, each with one fixed line chosen
by exception type and never built from ``str(exc)`` or the exception chain (PGD-15 AC-6):

* a refused or unusable test hook (``GMAIL_PDF_TEST_FAKE_MAILBOX``) exits 1 and is final: it is
  never retried as real mode, so no sign-in or network call can follow it;
* real mode, where no Gmail adapter is wired yet, exits 3 (interim, until STORY-01.04/01.06);
* a date that is not ``YYYY-MM-DD`` or a lone ``--start``/``--end`` exits 2 before anything
  else; an unknown zone or an end day before the start day exits 2 on the test hook, but in
  real mode ``build_deps`` fails first and they exit 3 (interim, decision 4; PGD-16 is asked
  to move these checks ahead of ``build_deps``).
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from gmail_pdf import __version__, redaction
from gmail_pdf.app import runner
from gmail_pdf.app.ports import Deps
from gmail_pdf.bootstrap import build_deps
from gmail_pdf.cli import args, console
from gmail_pdf.domain import messages
from gmail_pdf.domain.errors import (
    AdapterUnavailableError,
    FakeMailboxHookRefusedError,
    FakeMailboxNotImportableError,
    FakeMailboxUnavailableError,
    GmailPdfError,
    InputValidationError,
)
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.domain.models import ExitCode, RunRequest

logger = logging.getLogger(__name__)

PROG = "gmail-pdf"
EXIT_OK = int(ExitCode.OK)
# The run did not complete cleanly: unexpected failure, Ctrl+C or a test-hook failure (D-21,
# the first line tells which).
EXIT_FAILURE = int(ExitCode.FAILURE)
EXIT_USAGE = int(ExitCode.USAGE)
EXIT_AUTH = int(ExitCode.AUTH_FAILED)

# Failures of ``build_deps``: (exception type, the one line to print, exit code). The first row
# whose type matches wins, so a subclass is listed before its base class. A refused or unusable
# test hook exits 1 and real mode exits 3; they must never be swapped (AC-6).
_BUILD_FAILURES: tuple[tuple[type[GmailPdfError], str, int], ...] = (
    (FakeMailboxHookRefusedError, messages.FAKE_MAILBOX_HOOK_REFUSED_LINE, EXIT_FAILURE),
    (FakeMailboxNotImportableError, messages.FAKE_MAILBOX_NOT_IMPORTABLE_LINE, EXIT_FAILURE),
    (FakeMailboxUnavailableError, messages.FAKE_MAILBOX_UNREADABLE_LINE, EXIT_FAILURE),
    (AdapterUnavailableError, messages.SIGN_IN_UNAVAILABLE_LINE, EXIT_AUTH),
)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser (``-h/--help`` and the date-range options)."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Download every PDF attachment from one Gmail account for a date range. "
            "Access is read-only."
        ),
        epilog=f"gmail-pdf {__version__}",
    )
    args.add_arguments(parser)
    return parser


def _exit_code(exc: SystemExit) -> int:
    """Translate the ``SystemExit`` argparse raises into an integer exit code."""
    code = exc.code
    if code is None:
        return EXIT_OK
    return code if isinstance(code, int) else EXIT_USAGE


def _report_invalid_input(exc: InputValidationError) -> int:
    """Print the rejection (a fixed sentence that never echoes the input) and exit 2."""
    line = f"error: {redaction.safe_message(exc)}"
    # INFO, not ERROR: no log handler exists yet and an ERROR record would reach stderr a
    # second time through ``logging.lastResort``. The line is the whole story (no exc_info).
    logger.info("%s", line)
    console.print_error_line(line)
    return EXIT_USAGE


def _report_build_failure(exc: GmailPdfError) -> int:
    """Print the fixed line for a failed ``build_deps`` and return its exit code (1 or 3).

    The line is chosen by the exception's type only. Nothing from the exception is printed or
    logged: its message names a setting, and its ``__cause__`` / ``__context__`` hold the OS
    error text with the file path.
    """
    line, code = next(
        (line, code) for error_type, line, code in _BUILD_FAILURES if isinstance(exc, error_type)
    )
    # INFO, not ERROR, for the reason given in ``_report_invalid_input``; no exc_info.
    logger.info("%s", line)
    console.print_error_line(line)
    return code


def _execute(request: RunRequest, deps: Deps) -> int:
    """Run the selection and print the interim summary."""
    try:
        summary = runner.run(request, deps, console.ConsoleSink(), CancelToken())
    except InputValidationError as exc:
        return _report_invalid_input(exc)
    console.print_summary(summary)
    return int(summary.exit_code)


def _run(argv: Sequence[str] | None) -> int:
    """Parse the arguments and run; returns the exit code."""
    parser = build_parser()
    try:
        namespace = parser.parse_args(argv)
    except SystemExit as exc:  # argparse exits for --help and for usage errors
        return _exit_code(exc)
    try:
        request = args.requested_range(namespace)
    except InputValidationError as exc:
        return _report_invalid_input(exc)
    if request is None:
        parser.print_help()
        return EXIT_OK
    # ``build_deps`` comes before any other adapter work. Its failures are final: they are not
    # caught and retried as real mode, so no sign-in or network call can follow them.
    try:
        deps = build_deps()
    except (FakeMailboxHookRefusedError, AdapterUnavailableError) as exc:
        return _report_build_failure(exc)
    return _execute(request, deps)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line and return the process exit code.

    The first action is to install the redaction hooks; they stay installed for the rest of
    the process.

    Args:
        argv: Arguments after the program name; ``sys.argv[1:]`` when ``None``.

    Returns:
        0 on success (including ``--help``), 1 for an unexpected failure, Ctrl+C or a refused
        or unusable test hook, 2 for a usage error, a bad date format, or (on the test hook
        only) an unknown zone or a reversed range, 3 when Gmail sign-in is not available (in
        real mode this includes an unknown zone and a reversed range, for now).
    """
    redaction.install_logging_redaction()
    redaction.install_excepthooks()
    try:
        return _run(argv)
    except KeyboardInterrupt:
        redaction.report_cancelled()
        return EXIT_FAILURE
    except Exception as exc:  # last line of defence: nothing but the fixed line may escape
        redaction.report_unexpected_failure(type(exc), exc, exc.__traceback__)
        return EXIT_FAILURE


def entry() -> int:
    """Console-script entry point (``gmail-pdf``); the generated wrapper calls ``sys.exit``."""
    return main(sys.argv[1:])
