"""Command-line options of the date-range slice (architecture 4.2).

Only ``--start``, ``--end`` and ``--tz`` exist so far; the full flag table of the requirements
document (FR-045) and the rule for unknown flags beyond argparse's own exit 2 are STORY-07.01.
This module hands the typed values to ``domain.validation`` and holds no rule or sentence of its
own (STORY-02.03): the flag names below are the names its messages use (STD-55).
"""

from __future__ import annotations

import argparse
from collections.abc import Callable

from gmail_pdf.domain.validation import FieldNames, RawInput

FLAG_START = "--start"
FLAG_END = "--end"
FLAG_TZ = "--tz"
FIELD_NAMES = FieldNames(start=FLAG_START, end=FLAG_END, tz=FLAG_TZ)


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


def dates_given(namespace: argparse.Namespace) -> bool:
    """Whether ``--start`` or ``--end`` was given (with neither, the caller shows the usage)."""
    return (
        getattr(namespace, "start", None) is not None or getattr(namespace, "end", None) is not None
    )


def raw_input(namespace: argparse.Namespace, system_zone: Callable[[], str | None]) -> RawInput:
    """The typed values, ready for ``domain.validation.validate``.

    Args:
        namespace: The parsed options.
        system_zone: Returns the system zone's IANA name, or ``None`` when it cannot be found.
            It is called only when ``--tz`` was not given.
    """
    typed_zone = getattr(namespace, "tz", None)
    return RawInput(
        start=getattr(namespace, "start", None),
        end=getattr(namespace, "end", None),
        zone_name=system_zone() if typed_zone is None else typed_zone,
        names=FIELD_NAMES,
    )
