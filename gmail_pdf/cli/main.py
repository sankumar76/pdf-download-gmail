"""Command-line entry points.

``main(argv)`` is the single entry used by the ``gmail-pdf`` console script, by
``python -m gmail_pdf`` and by the repo-root ``gmail_pdf_downloader.py`` shim (ADR-005).

The walking skeleton understands ``-h/--help`` only. Parsing happens before any path
resolution, credential read, logging set-up or network call (PD-16), so ``--help`` is
always safe to run. The full flag table arrives with STORY-07.01.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from gmail_pdf import __version__

PROG = "gmail-pdf"
EXIT_OK = 0
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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line and return the process exit code.

    Args:
        argv: Arguments after the program name; ``sys.argv[1:]`` when ``None``.

    Returns:
        0 on success (including ``--help``), 2 for a usage error.
    """
    parser = build_parser()
    try:
        parser.parse_args(argv)
    except SystemExit as exc:  # argparse exits for --help and for usage errors
        return _exit_code(exc)
    # Nothing to run yet in the skeleton: show the usage and stop cleanly.
    parser.print_help()
    return EXIT_OK


def entry() -> int:
    """Console-script entry point (``gmail-pdf``); the generated wrapper calls ``sys.exit``."""
    return main(sys.argv[1:])
