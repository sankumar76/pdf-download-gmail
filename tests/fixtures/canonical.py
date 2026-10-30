"""Canonical synthetic mailboxes (test-strategy section 3, AC-7).

* ``rd_example_table()``: the six rows of the requirements document section 4.4 example, in
  processing order (oldest first), with the file name each row must be saved as.
* ``boundary_cases()``: messages on and around the edges of a one-day range.
* ``dst_cases()``: the same edges on the two 2026 DST transition days in ``America/New_York``
  (spring forward 2026-03-08, a 23-hour day; fall back 2026-11-01, a 25-hour day).

All content is synthetic (``example.com``).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from tests.fakes.fake_gmail import FakeMessage
from tests.fixtures.builders import MessageBuilder

NEW_YORK = "America/New_York"


@dataclass(frozen=True, slots=True)
class ExampleRow:
    """One row of the RD section 4.4 table."""

    message: FakeMessage
    original_name: str | None
    expected_saved_name: str
    reason: str


@dataclass(frozen=True, slots=True)
class RangeCase:
    """A message and whether it belongs to the one-day range ``day`` in ``tz``."""

    label: str
    message: FakeMessage
    day: str  # YYYY-MM-DD, the range is that single calendar day
    tz: str
    in_range: bool


def rd_example_table() -> list[ExampleRow]:
    """The RD section 4.4 example. Messages are received at 10:00, 11:00 or 12:00 UTC so that
    the date prefix is the same in any zone from UTC-10 to UTC+11 and the order is fixed."""
    rows = [
        ("m-0115-a", "2026-01-15T10:00:00", "Invoice.pdf", "20260115_Invoice.pdf", "First"),
        ("m-0115-b", "2026-01-15T11:00:00", "Invoice.pdf", "20260115_Invoice_1.pdf", "Same name"),
        ("m-0115-c", "2026-01-15T12:00:00", "invoice.PDF", "20260115_invoice_2.pdf", "Case"),
        ("m-0116", "2026-01-16T10:00:00", "Invoice.pdf", "20260116_Invoice.pdf", "Other date"),
        (
            "m-0120",
            "2026-01-20T10:00:00",
            "../../Report:Q4.pdf",
            "20260120_Report_Q4.pdf",
            "Path stripped, ':' replaced",
        ),
        ("m-0121", "2026-01-21T10:00:00", None, "20260121_attachment.pdf", "Default name"),
    ]
    return [
        ExampleRow(
            MessageBuilder(message_id).received(received).pdf(name).build(),
            name,
            saved_as,
            reason,
        )
        for message_id, received, name, saved_as, reason in rows
    ]


def _case(
    label: str, local_iso: str, day: str, in_range: bool, *, fold: int = 0, tz: str = NEW_YORK
) -> RangeCase:
    message = (
        MessageBuilder(f"{day}-{label}")
        .received(local_iso, tz, fold=fold)
        .subject(label)
        .pdf("Edge.pdf")
        .build()
    )
    return RangeCase(label, message, day, tz, in_range)


def boundary_cases(day: str = "2026-01-15", tz: str = NEW_YORK) -> list[RangeCase]:
    """Messages at the edges of the single-day range ``day`` (an ordinary, 24-hour day)."""
    previous, following = _neighbour_days(day)
    return [
        _case("day-before-end", f"{previous}T23:59:59", day, False, tz=tz),
        _case("start-00-00-00", f"{day}T00:00:00", day, True, tz=tz),
        _case("end-23-59-59", f"{day}T23:59:59", day, True, tz=tz),
        _case("next-day-00-00-00", f"{following}T00:00:00", day, False, tz=tz),
    ]


def dst_cases() -> list[RangeCase]:
    """Edges on the spring-forward and fall-back days in ``America/New_York``."""
    spring, fall = "2026-03-08", "2026-11-01"
    return [
        *boundary_cases(spring),
        *boundary_cases(fall),
        # The 01:30 wall-clock time occurs twice on the fall-back day (EDT, then EST).
        _case("fall-01-30-first", f"{fall}T01:30:00", fall, True, fold=0),
        _case("fall-01-30-second", f"{fall}T01:30:00", fall, True, fold=1),
    ]


def _neighbour_days(day: str) -> tuple[str, str]:
    current = date.fromisoformat(day)
    return (current - timedelta(days=1)).isoformat(), (current + timedelta(days=1)).isoformat()
