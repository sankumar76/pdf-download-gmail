"""The only module that prints (coding-standards section 10; architecture 4.2).

Every line passes through ``redaction.redact`` on its way out, so nothing a run prints can carry
a registered secret or a token shape, whatever built the line. Result lines go to stdout;
errors and notices go to stderr.

The ``Messages in range`` line is interim (assumption A-5 of PGD-15): STORY-07.04 replaces it
with the FR-042 summary and the progress lines of STORY-06.x join this module. A run that finds
nothing prints ``No PDFs found`` and ``0 PDFs found.`` instead of that line (PGD-17).
"""

from __future__ import annotations

import atexit
import os
import sys
from typing import TextIO

from gmail_pdf import redaction
from gmail_pdf.domain import events, messages
from gmail_pdf.domain.models import RunResult, RunSummary

_GUARD_INSTALLED = False


def _point_at_null(stream: TextIO) -> None:
    """Point ``stream``'s descriptor at the null device, so later flushes succeed.

    A stream without a descriptor (``StringIO``, ``pythonw``) has nothing to redirect and
    nothing the interpreter flushes at shutdown, so it is left alone.
    """
    try:
        descriptor = stream.fileno()
    except (AttributeError, OSError, ValueError):
        return
    null = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(null, descriptor)
    finally:
        os.close(null)


def _flush_standard_streams() -> None:
    """Flush stdout and stderr, discarding what a closed pipe can no longer take.

    Python exits 120 when the interpreter cannot flush a standard stream at shutdown, even
    when every write already failed and was ignored (PGD-68). The flush here finds the closed
    pipe first: redirecting its descriptor to the null device lets the interpreter's own
    flush at shutdown succeed, so the status the run chose survives -- 0 for ``--help``, 1 for
    a reported failure.
    """
    for stream in (sys.stdout, sys.stderr):
        if stream is None:
            continue
        try:
            stream.flush()
        except (OSError, ValueError):
            _point_at_null(stream)


def install_shutdown_flush_guard() -> None:
    """Make the interpreter's shutdown flush of stdout and stderr unable to change the exit code.

    Registered once per process, however often ``main`` runs. The guard is installed before
    any output, since the flush error it prevents happens after ``main`` has returned.
    """
    global _GUARD_INSTALLED
    if _GUARD_INSTALLED:
        return
    atexit.register(_flush_standard_streams)
    _GUARD_INSTALLED = True


def _write(stream: TextIO | None, line: str) -> None:
    """Print one redacted line; a missing or closed stream is not an error."""
    if stream is None:  # pythonw has no standard streams; ``print(file=None)`` would use stdout
        return
    try:
        print(redaction.redact(line), file=stream, flush=True)
    except (OSError, ValueError):
        # A closed pipe (``... | head``): the reader is gone and there is nowhere else to say so.
        return


def print_error_line(line: str) -> None:
    """Print one complete error line (it already starts with ``error: ``) to stderr."""
    _write(sys.stderr, line)


def print_warning_line(text: str) -> None:
    """Print ``warning: <text>`` to stderr; the run goes on."""
    _write(sys.stderr, f"warning: {text}")


def print_summary(summary: RunSummary) -> None:
    """Print the interim outcome of a run: the empty-range lines, the count or the cancel notice."""
    if summary.is_empty:
        _write(sys.stdout, messages.NO_PDFS_FOUND)
        _write(sys.stdout, messages.ZERO_PDFS_LINE)
    elif summary.result is RunResult.COMPLETED:
        _write(sys.stdout, messages.MESSAGES_IN_RANGE_TEMPLATE.format(count=len(summary.messages)))
    else:
        _write(sys.stderr, messages.RUN_CANCELLED_LINE)


class ConsoleSink:
    """The ``EventSink`` of the command line: notices become ``warning:`` lines on stderr."""

    def emit(self, event: events.Warning) -> None:
        """Print a warning as ``warning: <text>`` (the code name while no text is set)."""
        print_warning_line(event.text or event.code.name.lower())
