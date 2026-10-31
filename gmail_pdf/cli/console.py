"""The only module that prints (coding-standards section 10; architecture 4.2).

Every line passes through ``redaction.redact`` on its way out, so nothing a run prints can carry
a registered secret or a token shape, whatever built the line. Result lines go to stdout;
errors and notices go to stderr.

The ``Messages in range`` line is interim (assumption A-5 of PGD-15): STORY-07.04 replaces it
with the FR-042 summary and the progress lines of STORY-06.x join this module.
"""

from __future__ import annotations

import sys
from typing import TextIO

from gmail_pdf import redaction
from gmail_pdf.domain import events, messages
from gmail_pdf.domain.models import RunResult, RunSummary


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


def print_summary(summary: RunSummary) -> None:
    """Print the interim outcome of a run: the message count, or the cancel notice."""
    if summary.result is RunResult.COMPLETED:
        _write(sys.stdout, messages.MESSAGES_IN_RANGE_TEMPLATE.format(count=len(summary.messages)))
    else:
        _write(sys.stderr, messages.RUN_CANCELLED_LINE)


class ConsoleSink:
    """The ``EventSink`` of the command line: notices become ``warning:`` lines on stderr."""

    def emit(self, event: events.Warning) -> None:
        """Print a warning as ``warning: <text>`` (the code name while no text is set)."""
        _write(sys.stderr, f"warning: {event.text or event.code.name.lower()}")
