"""The inclusive date range as epoch seconds (FR-008, FR-012, architecture 6.2 and 6.6).

A range names whole calendar days in one time zone. ``start`` is the first second of the first
day; ``end`` is the first second of the day *after* the last day, taken as the next calendar
day at 00:00 in the zone (never ``+86400``), so a 23-hour or 25-hour daylight-saving day is
still exactly one day. ``contains`` is the exact local check that backs the widened Gmail query
(FR-012).

This module is pure: the zone object is handed in (``infra.tz`` resolves names), and the only
imports are the standard library and ``domain.messages`` / ``domain.errors``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, tzinfo

from gmail_pdf.domain import messages
from gmail_pdf.domain.errors import InputValidationError

# Strict ISO form (NFR-024): ASCII digits only. ``\d`` and ``date.fromisoformat`` alone accept
# other digit scripts and, on newer Pythons, other ISO forms such as ``20260101``.
_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_MS_PER_SECOND = 1000


def parse_iso_date(text: str, flag: str) -> date:
    """Parse ``YYYY-MM-DD`` strictly.

    Args:
        text: The value as typed.
        flag: The option name used in the rejection sentence (for example ``--start``). It
            comes from the program, never from the user.

    Raises:
        InputValidationError: ``text`` is not a real calendar date in that exact form. The
            message does not echo ``text``.
    """
    if _ISO_DATE.fullmatch(text) is not None:
        try:
            return date.fromisoformat(text)
        except ValueError:
            pass  # right shape, not a real date (month 13, 30 February, year 0000)
    raise InputValidationError(messages.DATE_FORMAT_TEMPLATE.format(flag=flag))


def _midnight_epoch(day: date, zone: tzinfo) -> int:
    """Epoch seconds of 00:00:00 on ``day`` in ``zone`` (first occurrence, ``fold=0``)."""
    return int(datetime.combine(day, time.min, tzinfo=zone).timestamp())


@dataclass(frozen=True, slots=True)
class DateRange:
    """Half-open range ``[start_epoch_s, end_epoch_s)`` covering whole local calendar days.

    Attributes:
        start_epoch_s: ``S``, epoch seconds of 00:00:00 on the first day.
        end_epoch_s: ``E``, epoch seconds of 00:00:00 on the day after the last day.
    """

    start_epoch_s: int
    end_epoch_s: int

    @classmethod
    def from_days(cls, first_day: date, last_day: date, zone: tzinfo) -> DateRange:
        """Build the range covering ``first_day`` to ``last_day`` inclusive in ``zone``.

        Raises:
            InputValidationError: ``last_day`` is before ``first_day``, or a day is outside the
                dates the platform can represent.
        """
        if last_day < first_day:
            raise InputValidationError(messages.END_BEFORE_START)
        try:
            day_after = last_day + timedelta(days=1)
            return cls(_midnight_epoch(first_day, zone), _midnight_epoch(day_after, zone))
        except (OverflowError, OSError, ValueError) as exc:
            raise InputValidationError(messages.DATE_OUT_OF_RANGE) from exc

    def contains(self, internal_date_ms: int) -> bool:
        """Whether a message received at ``internal_date_ms`` (epoch ms) is in the range."""
        return (
            self.start_epoch_s * _MS_PER_SECOND
            <= internal_date_ms
            < self.end_epoch_s * _MS_PER_SECOND
        )
