"""The inclusive date range as epoch seconds (FR-008, FR-012, architecture 6.2 and 6.6).

A range names whole calendar days in one time zone. ``start`` is the first second of the first
day; ``end`` is the first second of the day *after* the last day, taken as the next calendar
day at 00:00 in the zone (never ``+86400``), so a 23-hour or 25-hour daylight-saving day is
still exactly one day. ``contains`` is the exact local check that backs the widened Gmail query
(FR-012).

This module is pure: the zone object is handed in (``infra.tz`` resolves names), and the only
imports are the standard library. It trusts its input: the rules for what a user may ask for
(format, bounds, order, zone) are ``domain.validation``'s, and a range that reaches here has
passed them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, tzinfo

_MS_PER_SECOND = 1000


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
            ValueError: ``last_day`` is before ``first_day``, or the first day starts before
                1970-01-01T00:00:01Z, so ``after:<S-1>`` would be negative. A programming
                error: ``domain.validation`` rejects such input with a sentence first.
        """
        if last_day < first_day:
            raise ValueError("last_day is before first_day")
        start = _midnight_epoch(first_day, zone)
        if start < 1:
            raise ValueError("first_day starts before the epoch")
        return cls(start, _midnight_epoch(last_day + timedelta(days=1), zone))

    def contains(self, internal_date_ms: int) -> bool:
        """Whether a message received at ``internal_date_ms`` (epoch ms) is in the range."""
        return (
            self.start_epoch_s * _MS_PER_SECOND
            <= internal_date_ms
            < self.end_epoch_s * _MS_PER_SECOND
        )
