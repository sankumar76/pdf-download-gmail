"""Command-line entry points.

``main(argv)`` is the single entry used by the ``gmail-pdf`` console script, by
``python -m gmail_pdf`` and by the repo-root ``gmail_pdf_downloader.py`` shim (ADR-005).

Parsing happens before any path resolution, credential read, logging set-up or network call
(PD-16), so ``--help`` is always safe to run. Without ``--start`` and ``--end`` the usage text is
shown. With them the order is fixed: parse, validate, ``build_deps``, run (PGD-16). Validation
(``domain.validation``) needs no ``Deps``, so a bad input exits 2 in every mode before any
credential is read, any folder or file is created or any Google call is made; the full flag
table arrives with STORY-07.01.

Redaction comes first (PGD-13 AC-7): ``main`` installs the logging caps and the excepthooks
before the parser is built, so no log record or uncaught exception exists without them.
``argparse`` usage errors, an unknown or abbreviated flag among them, are not redacted yet (issue
#23). A failure that escapes the run prints one fixed line and exits 1; Ctrl+C prints
``Run cancelled`` and also exits 1 (decision D-21).

Expected failures are handled before that last line of defence, each with one fixed line chosen
by exception type and never built from ``str(exc)`` or the exception chain (PGD-15 AC-6):

* invalid input (a date that is not ``YYYY-MM-DD``, a date outside 1970-01-02..9999-12-30, a lone
  ``--start`` or ``--end``, an end day before the start day, an unknown zone) exits 2, with one
  line per problem and a ``warning:`` line, if the end day is in the future, when it is valid;
* a refused or unusable test hook (``GMAIL_PDF_TEST_FAKE_MAILBOX``) exits 1 and is final: it is
  never retried as real mode, so no sign-in or network call can follow it;
* real mode, where no Gmail adapter is wired yet, exits 3 (interim, until STORY-01.04/01.06).

A range with no matching mail is not a failure: the run finishes, prints ``No PDFs found`` and
``0 PDFs found.`` and exits 0 (PGD-17). A failed list call is the opposite: its error reaches the
last-resort handler below, so stdout stays empty and stderr carries the one fixed error line and
no retry notice (AC-4).
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from gmail_pdf import __version__, redaction
from gmail_pdf.app import runner
from gmail_pdf.app.ports import Deps
from gmail_pdf.bootstrap import SystemClock, build_deps, system_zone_name
from gmail_pdf.cli import args, console
from gmail_pdf.domain import messages, validation
from gmail_pdf.domain.errors import (
    AdapterUnavailableError,
    FakeMailboxHookRefusedError,
    FakeMailboxNotImportableError,
    FakeMailboxUnavailableError,
    GmailPdfError,
)
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.domain.models import ExitCode, RunRequest

logger = logging.getLogger(__name__)

PROG = "gmail-pdf"
# The retry helper logs each retry at WARNING (PGD-15 AC-7). Until the run log exists
# (STORY-07.02) those records are log content, not user output (PGD-17 AC-4, C40, issue #40).
_RETRY_LOGGER = "gmail_pdf.infra.retry"
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
        # An abbreviation would change meaning the day a flag is added (OQ-3, FR-045): an
        # abbreviated flag is an unknown flag and exits 2.
        allow_abbrev=False,
    )
    args.add_arguments(parser)
    return parser


def _exit_code(exc: SystemExit) -> int:
    """Translate the ``SystemExit`` argparse raises into an integer exit code."""
    code = exc.code
    if code is None:
        return EXIT_OK
    return code if isinstance(code, int) else EXIT_USAGE


def _keep_retry_records_off_stderr() -> None:
    """Give the retry logger a handler of its own, so ``logging.lastResort`` is not used for it.

    With no handler anywhere, Python prints a record of WARNING or higher to stderr through
    ``lastResort``: five ``Retrying ...`` lines would precede the one error line (issue #40).
    A ``NullHandler`` on this logger only counts as "a handler was found"; it prints nothing.
    The records still propagate, so the run log handler of STORY-07.02 receives them. Every
    other logger, ``gmail_pdf`` ones included, keeps the redacted ``lastResort`` fallback, and
    the handler is added once however often ``main`` runs.
    """
    retry_logger = logging.getLogger(_RETRY_LOGGER)
    if not any(isinstance(handler, logging.NullHandler) for handler in retry_logger.handlers):
        retry_logger.addHandler(logging.NullHandler())


def _report_invalid_input(errors: tuple[str, ...]) -> int:
    """Print each rejection and exit 2.

    No sentence echoes raw input; the reversed-range sentence prints the two parsed dates (AC-2).
    """
    for sentence in errors:
        line = f"error: {sentence}"
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
    # INFO, not ERROR: see ``_report_invalid_input``; no exc_info.
    logger.info("%s", line)
    console.print_error_line(line)
    return code


def _execute(request: RunRequest, deps: Deps) -> int:
    """Run the selection and print the interim summary."""
    summary = runner.run(request, deps, console.ConsoleSink(), CancelToken())
    console.print_summary(summary)
    return int(summary.exit_code)


def _run(argv: Sequence[str] | None) -> int:
    """Parse the arguments and run; returns the exit code."""
    parser = build_parser()
    try:
        namespace = parser.parse_args(argv)
    except SystemExit as exc:  # argparse exits for --help and for usage errors
        return _exit_code(exc)
    if not args.dates_given(namespace):
        parser.print_help()
        return EXIT_OK
    result = validation.validate(args.raw_input(namespace, system_zone_name), SystemClock().today)
    if result.request is None:
        return _report_invalid_input(result.errors)
    for warning in result.warnings:
        console.print_warning_line(warning)
    # ``build_deps`` comes after validation, so invalid input never reaches it, and before any
    # other adapter work. Its failures are final: they are not caught and retried as real mode,
    # so no sign-in or network call can follow them.
    try:
        deps = build_deps()
    except (FakeMailboxHookRefusedError, AdapterUnavailableError) as exc:
        return _report_build_failure(exc)
    return _execute(result.request, deps)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line and return the process exit code.

    The first action is to install the redaction hooks; they stay installed for the rest of
    the process.

    Args:
        argv: Arguments after the program name; ``sys.argv[1:]`` when ``None``.

    Returns:
        0 on success (including ``--help``), 1 for an unexpected failure, Ctrl+C or a refused
        or unusable test hook, 2 for a usage error or invalid input (a bad date, a reversed
        range, an unknown zone: the same in every mode), 3 when Gmail sign-in is not available.
    """
    redaction.install_logging_redaction()
    redaction.install_excepthooks()
    _keep_retry_records_off_stderr()
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
