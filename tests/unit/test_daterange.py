"""PGD-15 AC-1, AC-3 and AC-10: the inclusive date range as epoch seconds.

Expected values are literals, worked out from the UTC offset of the zone on that day (and not
with the code under test), so a wrong implementation cannot agree with its own test. Zones are
fixed in every test; nothing depends on the machine's zone.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from zoneinfo import ZoneInfo

import pytest

from gmail_pdf.domain import messages
from gmail_pdf.domain.daterange import DateRange, parse_iso_date
from gmail_pdf.domain.errors import InputValidationError
from gmail_pdf.infra import tz as tz_module

pytestmark = pytest.mark.req("FR-008", "FR-012")

KOLKATA = ZoneInfo("Asia/Kolkata")
NEW_YORK = ZoneInfo("America/New_York")


def days(first: str, last: str, zone: ZoneInfo) -> DateRange:
    return DateRange.from_days(date.fromisoformat(first), date.fromisoformat(last), zone)


# ----------------------------------------------------------------------------------- AC-1
@pytest.mark.req("AC-1")
def test_kolkata_january_runs_from_local_midnight_to_the_next_local_midnight() -> None:
    date_range = days("2026-01-01", "2026-01-31", KOLKATA)

    # 2026-01-01T00:00:00+05:30 and 2026-02-01T00:00:00+05:30
    assert (date_range.start_epoch_s, date_range.end_epoch_s) == (1767205800, 1769884200)


@pytest.mark.req("AC-1")
@pytest.mark.parametrize(
    ("first", "last", "zone", "start", "end"),
    [
        pytest.param("2026-01-01", "2026-01-01", NEW_YORK, 1767243600, 1767330000, id="one-day"),
        pytest.param(
            "2026-01-01",
            "2026-01-01",
            ZoneInfo("Pacific/Kiritimati"),
            1767175200,
            1767261600,
            id="utc-plus-14",
        ),
        pytest.param(
            "2028-02-29", "2028-02-29", ZoneInfo("UTC"), 1835395200, 1835481600, id="leap-day"
        ),
        pytest.param(
            "2025-12-31", "2025-12-31", ZoneInfo("UTC"), 1767139200, 1767225600, id="year-end"
        ),
    ],
)
def test_edge_ranges_in_fixed_zones(
    first: str, last: str, zone: ZoneInfo, start: int, end: int
) -> None:
    date_range = days(first, last, zone)

    assert (date_range.start_epoch_s, date_range.end_epoch_s) == (start, end)


# ----------------------------------------------------------------------------------- AC-3
SPRING_START, SPRING_END = 1772946000, 1773028800  # 2026-03-08 in New York, a 23-hour day
FALL_START, FALL_END = 1793505600, 1793595600  # 2026-11-01 in New York, a 25-hour day
SPAN_START, SPAN_END = SPRING_START, 1793595600


@pytest.mark.req("AC-3")
@pytest.mark.parametrize(
    ("first", "last", "start", "end", "hours"),
    [
        pytest.param("2026-03-08", "2026-03-08", SPRING_START, SPRING_END, 23, id="spring-forward"),
        pytest.param("2026-11-01", "2026-11-01", FALL_START, FALL_END, 25, id="fall-back"),
        pytest.param("2026-03-08", "2026-11-01", SPAN_START, SPAN_END, None, id="spanning-both"),
    ],
)
def test_new_york_dst_days_are_calendar_days_not_86400_seconds(
    first: str, last: str, start: int, end: int, hours: int | None
) -> None:
    date_range = days(first, last, NEW_YORK)

    assert (date_range.start_epoch_s, date_range.end_epoch_s) == (start, end)
    if hours is not None:
        assert date_range.end_epoch_s - date_range.start_epoch_s == hours * 3600


@pytest.mark.req("AC-3")
@pytest.mark.parametrize(
    ("first", "last", "start", "end"),
    [
        pytest.param("2026-03-08", "2026-03-08", SPRING_START, SPRING_END, id="spring-forward"),
        pytest.param("2026-11-01", "2026-11-01", FALL_START, FALL_END, id="fall-back"),
        pytest.param("2026-03-08", "2026-11-01", SPAN_START, SPAN_END, id="spanning-both"),
    ],
)
def test_the_last_second_of_the_end_day_is_in_and_the_next_midnight_is_out(
    first: str, last: str, start: int, end: int
) -> None:
    date_range = days(first, last, NEW_YORK)

    assert date_range.contains(start * 1000)  # 00:00:00 on the first day
    assert not date_range.contains(start * 1000 - 1)
    assert date_range.contains(end * 1000 - 1000)  # 23:59:59 local on the last day
    assert date_range.contains(end * 1000 - 1)
    assert not date_range.contains(end * 1000)  # 00:00:00 the next local day


@pytest.mark.req("AC-2")
def test_contains_is_half_open_at_millisecond_precision() -> None:
    date_range = DateRange(100, 200)

    assert [date_range.contains(ms) for ms in (99_999, 100_000, 199_999, 200_000)] == [
        False,
        True,
        True,
        False,
    ]


# ------------------------------------------------------------------------- invalid ranges
def test_an_end_day_before_the_start_day_is_rejected() -> None:
    with pytest.raises(InputValidationError):
        days("2026-02-01", "2026-01-31", KOLKATA)


def test_the_last_representable_day_is_rejected_not_crashed() -> None:
    with pytest.raises(InputValidationError):
        DateRange.from_days(date.max, date.max, ZoneInfo("UTC"))


# ------------------------------------------------------------------------ strict parsing
@pytest.mark.parametrize("text", ["2026-01-01", "2028-02-29", "0001-01-01", "9999-12-31"])
def test_strict_iso_dates_are_accepted(text: str) -> None:
    assert parse_iso_date(text, "--start") == date.fromisoformat(text)


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("", id="empty"),
        pytest.param("2026-1-1", id="no-zero-padding"),
        pytest.param("20260101", id="basic-format"),
        pytest.param("2026-01-01\n", id="trailing-newline"),
        pytest.param(" 2026-01-01", id="leading-space"),
        pytest.param("2026/01/01", id="slashes"),
        pytest.param("2026-13-01", id="month-13"),
        pytest.param("2026-02-30", id="30-february"),
        pytest.param("2026-02-29", id="29-february-in-a-common-year"),
        pytest.param("0000-01-01", id="year-zero"),
        pytest.param("２０２６-01-01", id="fullwidth-digits"),
        pytest.param("٢٠٢٦-01-01", id="arabic-indic-digits"),
        pytest.param("2026-01-01T00:00:00", id="date-time"),
    ],
)
def test_anything_but_a_real_ascii_iso_date_is_rejected_without_echoing_it(text: str) -> None:
    with pytest.raises(InputValidationError) as exc_info:
        parse_iso_date(text, "--start")

    assert str(exc_info.value) == "--start must be a date written as YYYY-MM-DD."


# ----------------------------------------------------------------------------------- AC-10
@pytest.mark.req("AC-10")
@pytest.mark.parametrize(
    ("system_zone", "start", "end"),
    [
        pytest.param("Asia/Kolkata", 1767205800, 1769884200, id="kolkata"),
        pytest.param("America/New_York", 1767243600, 1769922000, id="new-york"),
    ],
)
def test_without_tz_the_system_zone_is_used(
    monkeypatch: pytest.MonkeyPatch, system_zone: str, start: int, end: int
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lambda: system_zone)

    date_range = DateRange.from_days(
        date(2026, 1, 1), date(2026, 1, 31), tz_module.resolve_zone(None)
    )

    assert (date_range.start_epoch_s, date_range.end_epoch_s) == (start, end)


@pytest.mark.req("AC-10")
def test_an_explicit_zone_wins_over_the_system_zone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lambda: "America/New_York")

    assert tz_module.resolve_zone("Asia/Kolkata") == KOLKATA


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("Mars/Olympus_Mons", id="unknown"),
        pytest.param("", id="empty"),
        pytest.param("../etc/passwd", id="path-traversal"),
        pytest.param("America", id="a-directory"),
        pytest.param("Asia/Kolkata\x00", id="nul-byte"),
    ],
)
def test_an_unknown_zone_name_is_an_input_error_that_does_not_echo_the_name(name: str) -> None:
    with pytest.raises(InputValidationError) as exc_info:
        tz_module.resolve_zone(name)

    assert str(exc_info.value) == messages.ZONE_UNKNOWN


def _system_zone_lookup_fails() -> str:
    raise OSError("no zone")


@pytest.mark.parametrize(
    "lookup",
    [
        pytest.param(lambda: "", id="empty-name"),
        pytest.param(_system_zone_lookup_fails, id="os-error"),
    ],
)
def test_an_unresolvable_system_zone_is_an_input_error(
    monkeypatch: pytest.MonkeyPatch, lookup: Callable[[], str]
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lookup)

    with pytest.raises(InputValidationError):
        tz_module.resolve_zone(None)
