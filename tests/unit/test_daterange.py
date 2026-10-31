"""PGD-15 AC-1, AC-3 and AC-10: the inclusive date range as epoch seconds.

Expected values are literals, worked out from the UTC offset of the zone on that day (and not
with the code under test), so a wrong implementation cannot agree with its own test. Zones are
fixed in every test; nothing depends on the machine's zone.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest

from gmail_pdf.domain.daterange import DateRange
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
        pytest.param(
            "2026-01-01",
            "2026-01-01",
            ZoneInfo("Pacific/Pago_Pago"),
            1767265200,
            1767351600,
            id="utc-minus-11",
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


# Midnight itself does not exist on the day the clocks go forward at 00:00: the day then starts
# at 01:00 local, the instant of 00:00 in the old offset, and a wrong ``fold`` starts it an hour
# early, inside the previous day. Worked out by hand from the offsets, not with the code.
MIDNIGHT_GAPS = [
    # Havana, 2026-03-08: 00:00 CST (UTC-5) = 05:00 UTC; the day ends 2026-03-09 00:00 CDT (UTC-4).
    pytest.param("America/Havana", "2026-03-08", 1772946000, 1773028800, id="havana"),
    # Cairo, 2026-04-24 (last Friday of April): 00:00 EET (UTC+2) = 22:00 UTC the day before.
    pytest.param("Africa/Cairo", "2026-04-24", 1776981600, 1777064400, id="cairo"),
    # Apia, 2011-12-30 was skipped altogether: the day starts and ends at the same instant.
    pytest.param("Pacific/Apia", "2011-12-30", 1325239200, 1325239200, id="apia-skipped-day"),
]


@pytest.mark.req("AC-3")
@pytest.mark.parametrize(("zone", "day", "start", "end"), MIDNIGHT_GAPS)
def test_a_day_whose_midnight_does_not_exist_starts_at_the_old_offsets_midnight(
    zone: str, day: str, start: int, end: int
) -> None:
    date_range = days(day, day, ZoneInfo(zone))

    assert (date_range.start_epoch_s, date_range.end_epoch_s) == (start, end)


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


# --------------------------------------------------------- the guards behind the validation
# The rules a user is held to (order, bounds 1970-01-02..9999-12-30) are ``domain.validation``'s.
# ``from_days`` only refuses what would build a wrong query, whoever calls it (PGD-16 AC-9).
def test_an_end_day_before_the_start_day_is_refused() -> None:
    with pytest.raises(ValueError):
        days("2026-02-01", "2026-01-31", KOLKATA)


@pytest.mark.req("AC-9")
@pytest.mark.parametrize(
    ("day", "zone"),
    [
        pytest.param("1970-01-01", "UTC", id="epoch-day-utc"),
        pytest.param("1970-01-01", "Asia/Kolkata", id="epoch-day-east-of-utc"),
        pytest.param("1969-12-31", "America/New_York", id="before-the-epoch-west-of-utc"),
        pytest.param("0001-01-01", "UTC", id="year-one"),
    ],
)
def test_a_first_day_that_starts_before_the_epoch_is_refused(day: str, zone: str) -> None:
    with pytest.raises(ValueError):
        days(day, "2026-12-31", ZoneInfo(zone))


@pytest.mark.req("AC-9")
def test_the_guard_sits_between_a_start_of_zero_and_a_start_of_one_second() -> None:
    # Fixed offsets of a second make the start fall exactly on either side of the guard.
    zero = timezone(timedelta(0))  # 1970-01-01T00:00:00Z: S = 0, after:-1
    one = timezone(timedelta(seconds=-1))  # 1970-01-01T00:00:00-00:00:01: S = 1, after:0

    with pytest.raises(ValueError):
        DateRange.from_days(date(1970, 1, 1), date(1970, 1, 1), zero)
    accepted = DateRange.from_days(date(1970, 1, 1), date(1970, 1, 1), one)

    assert (accepted.start_epoch_s, accepted.end_epoch_s) == (1, 86401)


@pytest.mark.req("AC-9")
def test_the_first_second_the_guard_accepts_gives_a_zero_after_bound() -> None:
    # 1970-01-02 00:00 in Etc/GMT-14 is 1970-01-01T10:00:00Z = 36000 s; in UTC it is 86400 s.
    far_east = days("1970-01-02", "1970-01-02", ZoneInfo("Etc/GMT-14"))
    utc = days("1970-01-02", "1970-01-02", ZoneInfo("UTC"))

    assert (far_east.start_epoch_s, far_east.end_epoch_s) == (36000, 122400)
    assert (utc.start_epoch_s, utc.end_epoch_s) == (86400, 172800)


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
def test_a_name_that_is_not_a_zone_is_not_resolved(name: str) -> None:
    # Whether a name is acceptable is ``domain.validation``'s call; the lookup just refuses it.
    with pytest.raises((ZoneInfoNotFoundError, ValueError, OSError)):
        tz_module.resolve_zone(name)


def _system_zone_lookup_fails() -> str:
    raise OSError("no zone")


@pytest.mark.parametrize(
    "lookup",
    [
        pytest.param(lambda: "", id="empty-name"),
        pytest.param(_system_zone_lookup_fails, id="os-error"),
    ],
)
def test_an_unresolvable_system_zone_has_no_name_and_cannot_be_resolved(
    monkeypatch: pytest.MonkeyPatch, lookup: Callable[[], str]
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lookup)

    assert tz_module.system_zone_name() is None
    # An empty name must not fall through to ``ZoneInfo("")``.
    with pytest.raises(ValueError, match="system time zone"):
        tz_module.resolve_zone(None)


def test_the_system_zone_name_is_the_one_tzlocal_reports(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lambda: "Asia/Kolkata")

    assert tz_module.system_zone_name() == "Asia/Kolkata"


def test_the_system_clock_reads_today_in_the_given_zone() -> None:
    clock = tz_module.SystemClock()
    before = date.today()

    far_east = clock.today(ZoneInfo("Pacific/Kiritimati"))  # UTC+14
    far_west = clock.today(ZoneInfo("Pacific/Pago_Pago"))  # UTC-11

    assert type(far_east) is date
    assert 1 <= (far_east - far_west).days <= 2  # 25 hours apart, whatever today is
    assert abs((far_east - before).days) <= 2
