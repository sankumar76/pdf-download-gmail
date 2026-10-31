"""Command-line options of the date-range slice (architecture 4.2).

Only ``--start``, ``--end`` and ``--tz`` exist so far; the full flag table of the requirements
document (FR-045) and the rule for unknown flags beyond argparse's own exit 2 are STORY-07.01.
Dates are parsed strictly here (NFR-024); the wording of every rejection is STORY-02.03.
"""

from __future__ import annotations

import argparse

from gmail_pdf.domain import messages
from gmail_pdf.domain.daterange import parse_iso_date
from gmail_pdf.domain.errors import InputValidationError
from gmail_pdf.domain.models import RunRequest

FLAG_START = "--start"
FLAG_END = "--end"
FLAG_TZ = "--tz"


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the date-range options to ``parser``."""
    parser.add_argument(
        FLAG_START,
        metavar="YYYY-MM-DD",
        help="First day of the range, inclusive, in the chosen time zone.",
    )
    parser.add_argument(
        FLAG_END,
        metavar="YYYY-MM-DD",
        help="Last day of the range, inclusive, in the chosen time zone.",
    )
    parser.add_argument(
        FLAG_TZ,
        metavar="ZONE",
        help="IANA time zone of the days above, for example Asia/Kolkata (default: system zone).",
    )


def requested_range(namespace: argparse.Namespace) -> RunRequest | None:
    """Turn parsed options into a request.

    Returns:
        The request, or ``None`` when neither ``--start`` nor ``--end`` was given (the caller
        shows the usage text, as the walking skeleton did).

    Raises:
        InputValidationError: only one of the two dates was given, or a date is not a real
            ``YYYY-MM-DD`` date. The message never echoes the value.
    """
    start_text = getattr(namespace, "start", None)
    end_text = getattr(namespace, "end", None)
    if start_text is None and end_text is None:
        return None
    if start_text is None or end_text is None:
        raise InputValidationError(messages.DATES_REQUIRED_TOGETHER)
    return RunRequest(
        parse_iso_date(start_text, FLAG_START),
        parse_iso_date(end_text, FLAG_END),
        getattr(namespace, "tz", None),
    )
