"""Input validation shared by every front end (FR-015, architecture 4.1 and 6.3).

``validate`` has no I/O of its own: it opens no connection and prints nothing. Its only read is
the time-zone database, which the zone check needs (AC-4): ``available_timezones()`` once, cached,
and the file of the chosen zone. It takes the three inputs as the user typed them and returns
every problem at once, with wording taken only from ``domain/messages.py`` (one table for the
command line and the window, FR-064). No sentence echoes raw input; the reversed-range sentence
prints the two parsed dates (AC-2).

Date rules (NFR-024, AC-9): the form is ``YYYY-MM-DD`` in ASCII digits and a real calendar
date; each date must also lie from ``EARLIEST_DATE`` to ``LATEST_DATE``, the same in every zone.
The floor keeps ``after:<S-1>`` from ever being negative: from 1970-01-02 the first second of
the day is at least 36000 in every zone (Etc/GMT-14 is the smallest). The ceiling keeps the day
after the end date representable: ``date.max`` has no next day.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, tzinfo
from functools import lru_cache
from zoneinfo import ZoneInfo, available_timezones

from gmail_pdf.domain import messages
from gmail_pdf.domain.models import RunRequest

# Rejected, not clamped: clamping would change the range the user typed without telling them,
# and the range names every file, the manifest and every re-run (PGD-16 AC-9, assumption A-4).
EARLIEST_DATE = date(1970, 1, 2)
LATEST_DATE = date(9999, 12, 30)

# ASCII only: ``\d`` alone matches other digit scripts (NFR-024). ``fullmatch`` is used, so a
# trailing newline does not slip through the way it would with ``$``.
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}", re.ASCII)


@dataclass(frozen=True, slots=True)
class FieldNames:
    """How the front end calls the three inputs in a message (the CLI: its flag names)."""

    start: str
    end: str
    tz: str


@dataclass(frozen=True, slots=True)
class RawInput:
    """The inputs as typed, before any check.

    Attributes:
        start: The start date text, or ``None`` when it was not given.
        end: The end date text, or ``None`` when it was not given.
        zone_name: The time zone name the run would use: what the user typed, else the name of
            the system zone, or ``None`` when no name could be found for it.
        names: How messages name the three inputs.
    """

    start: str | None
    end: str | None
    zone_name: str | None
    names: FieldNames


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """What ``validate`` found.

    Attributes:
        errors: One sentence per problem, in the order start, end, range, zone (AC-5). Empty
            when the input is valid.
        warnings: Notices for valid input (AC-3). Always empty when there are errors.
        request: The validated request, present exactly when ``errors`` is empty.
    """

    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    request: RunRequest | None = None


@lru_cache(maxsize=1)
def _known_zones() -> frozenset[str]:
    """Every IANA name ``zoneinfo`` knows; read once (it scans the time-zone database)."""
    return frozenset(available_timezones())


def parse_iso_date(text: str) -> date | None:
    """Parse ``YYYY-MM-DD`` strictly; ``None`` when ``text`` is not a real date in that form."""
    if _ISO_DATE.fullmatch(text) is None:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None  # right shape, not a real date (month 13, 30 February, year 0000)


def _check_date(text: str | None, name: str) -> tuple[date | None, str | None]:
    """The date, or the sentence that rejects ``text`` (a missing value counts as malformed)."""
    parsed = None if text is None else parse_iso_date(text)
    if parsed is None:
        return None, messages.DATE_NOT_ISO_TEMPLATE.format(field=name)
    if not EARLIEST_DATE <= parsed <= LATEST_DATE:
        return None, messages.DATE_OUT_OF_BOUNDS_TEMPLATE.format(
            field=name, earliest=EARLIEST_DATE.isoformat(), latest=LATEST_DATE.isoformat()
        )
    return parsed, None


def _check_zone(zone_name: str | None, name: str) -> tuple[ZoneInfo | None, str | None]:
    """The zone, or the sentence that rejects ``zone_name``.

    A name is valid only if it is a member of ``zoneinfo.available_timezones()``, as written:
    no trimming, no case folding, no separator conversion, so the answer is the same on every
    operating system.
    """
    if zone_name is None or zone_name not in _known_zones():
        return None, messages.ZONE_NOT_IANA_TEMPLATE.format(field=name)
    return ZoneInfo(zone_name), None


def validate(raw: RawInput, today: Callable[[tzinfo], date]) -> ValidationResult:
    """Check the inputs and report every problem at once.

    Args:
        raw: The inputs as typed.
        today: Returns today's date in the given zone (an injected clock; the check never reads
            the machine's clock itself).

    Returns:
        The problems in the order start, end, range (only when both dates are valid), zone; or,
        when there are none, the request and, if the end date is after today in the chosen
        zone, the future-end warning.
    """
    start, start_error = _check_date(raw.start, raw.names.start)
    end, end_error = _check_date(raw.end, raw.names.end)
    zone, zone_error = _check_zone(raw.zone_name, raw.names.tz)

    errors = [error for error in (start_error, end_error) if error is not None]
    if start is not None and end is not None and start > end:
        errors.append(
            messages.RANGE_REVERSED_TEMPLATE.format(
                start_field=raw.names.start,
                start=start.isoformat(),
                end_field=raw.names.end,
                end=end.isoformat(),
            )
        )
    if zone_error is not None:
        errors.append(zone_error)
    if errors or start is None or end is None or zone is None or raw.zone_name is None:
        return ValidationResult(tuple(errors), ())

    warnings = (messages.END_IN_FUTURE_WARNING,) if end > today(zone) else ()
    return ValidationResult((), warnings, RunRequest(start, end, raw.zone_name))
