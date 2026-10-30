"""Command-line entry points.

``main(argv)`` is the single entry used by the ``gmail-pdf`` console script, by
``python -m gmail_pdf`` and by the repo-root ``gmail_pdf_downloader.py`` shim (ADR-005).

The walking skeleton understands ``-h/--help`` only. Parsing happens before any path
resolution, credential read, logging set-up or network call (PD-16), so ``--help`` is
always safe to run. The full flag table arrives with STORY-07.01.

Redaction comes first (PGD-13 AC-7): ``main`` installs the logging caps and the excepthooks
before the parser is built, so no handler or argument output exists without them. A failure
that escapes the run prints one fixed line and exits 1; Ctrl+C prints ``Run cancelled`` and
also exits 1 (decision D-21).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from gmail_pdf import __version__, redaction

PROG = "gmail-pdf"
EXIT_OK = 0
# The run did not complete cleanly: unexpected failure or Ctrl+C (D-21, first line tells which).
EXIT_FAILURE = 1
EXIT_USAGE = 2


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser (``-h/--help`` only in the walking skeleton)."""
    return argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Download every PDF attachment from one Gmail account for a date range. "
            "Access is read-only."
        ),
        epilog=f"gmail-pdf {__version__}",
    )


def _exit_code(exc: SystemExit) -> int:
    """Translate the ``SystemExit`` argparse raises into an integer exit code."""
    code = exc.code
    if code is None:
        return EXIT_OK
    return code if isinstance(code, int) else EXIT_USAGE


def _run(argv: Sequence[str] | None) -> int:
    """Parse the arguments and run; returns the exit code."""
    parser = build_parser()
    try:
        parser.parse_args(argv)
    except SystemExit as exc:  # argparse exits for --help and for usage errors
        return _exit_code(exc)
    # Nothing to run yet in the skeleton: show the usage and stop cleanly.
    parser.print_help()
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line and return the process exit code.

    The first action is to install the redaction hooks; they stay installed for the rest of
    the process.

    Args:
        argv: Arguments after the program name; ``sys.argv[1:]`` when ``None``.

    Returns:
        0 on success (including ``--help``), 1 for an unexpected failure or Ctrl+C,
        2 for a usage error.
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
