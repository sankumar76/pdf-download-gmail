"""Shared inputs and expected sentences for the ``domain.validation`` tests.

Every expected sentence is a literal copied from the story (and ux-spec section 12), never read
back from ``domain/messages.py``. "Today" comes from a clock frozen at one instant.
"""

from __future__ import annotations

from datetime import datetime, timezone

from gmail_pdf.domain.validation import FieldNames, RawInput, ValidationResult, validate
from tests.fakes.fake_time import FixedInstantClock

NAMES = FieldNames(start="--start", end="--end", tz="--tz")

# 2026-01-15 10:00 UTC: 2026-01-16 in Pacific/Kiritimati (UTC+14), 2026-01-14 in Pago_Pago (UTC-11).
CLOCK = FixedInstantClock(datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc))

START_FORMAT = "--start: Enter the date as YYYY-MM-DD, for example 2026-01-31."

END_FORMAT = "--end: Enter the date as YYYY-MM-DD, for example 2026-01-31."

START_BOUNDS = "--start: Enter a date from 1970-01-02 to 9999-12-30."

END_BOUNDS = "--end: Enter a date from 1970-01-02 to 9999-12-30."

ZONE_ERROR = "--tz: Unknown time zone. Use an IANA name such as Asia/Kolkata."

FUTURE_END = "End date is in the future. Only mail received so far is included."


def raw(
    start: str | None = "2026-01-01", end: str | None = "2026-01-31", zone: str | None = "UTC"
) -> RawInput:
    return RawInput(start=start, end=end, zone_name=zone, names=NAMES)


def check(
    start: str | None = "2026-01-01", end: str | None = "2026-01-31", zone: str | None = "UTC"
) -> ValidationResult:
    return validate(raw(start, end, zone), CLOCK.today)
