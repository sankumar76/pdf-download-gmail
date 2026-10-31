"""PGD-16 AC-1..AC-5, AC-7 and AC-9: ``domain.validation`` and the single message table.

Every expected sentence is a literal copied from the story (and ux-spec section 12), never read
back from ``domain/messages.py``, so a changed sentence fails here. "Today" comes from a clock
frozen at one instant: nothing depends on the machine's date or zone.
"""

from __future__ import annotations

import ast
import re
from datetime import date, datetime, timezone, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo, available_timezones

import pytest

from gmail_pdf.cli import args
from gmail_pdf.domain import messages
from gmail_pdf.domain.daterange import DateRange
from gmail_pdf.domain.models import RunRequest
from gmail_pdf.domain.query import baseline_query
from gmail_pdf.domain.validation import (
    FieldNames,
    RawInput,
    ValidationResult,
    parse_iso_date,
    validate,
)
from tests.fakes.fake_time import FixedInstantClock
from tests.support import sentinels
from tests.support.subprocess_env import REPO_ROOT

pytestmark = pytest.mark.req("FR-015", "NFR-024")

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


# ----------------------------------------------------------------------------------- valid
@pytest.mark.req("AC-7")
def test_valid_input_gives_the_request_and_no_message() -> None:
    result = check("2026-01-01", "2026-01-10", "Asia/Kolkata")

    assert result == ValidationResult(
        (), (), RunRequest(date(2026, 1, 1), date(2026, 1, 10), "Asia/Kolkata")
    )


@pytest.mark.req("AC-2")
def test_start_equal_to_end_is_valid() -> None:
    assert check("2026-01-05", "2026-01-05").errors == ()


# ----------------------------------------------------------------------------------- AC-1
BAD_DATES = [
    pytest.param("2026-1-5", id="no-zero-padding"),
    pytest.param("2026/01/05", id="slashes"),
    pytest.param("05-01-2026", id="day-first"),
    pytest.param("2026-02-30", id="30-february"),
    pytest.param("2026-02-29", id="29-february-in-a-common-year"),
    pytest.param("2026-13-01", id="month-13"),
    pytest.param("0000-01-01", id="year-zero"),
    pytest.param("", id="empty"),
    pytest.param(" ", id="one-space"),
    pytest.param("   ", id="spaces"),
    pytest.param("\t\n", id="tab-and-newline"),
    pytest.param("20260105", id="basic-format"),
    pytest.param("2026-01-05\n", id="trailing-newline"),
    pytest.param(" 2026-01-05", id="leading-space"),
    pytest.param("2026-01-05T00:00:00", id="date-time"),
    pytest.param("٢٠٢٦-٠١-٠٥", id="arabic-indic-digits"),
    pytest.param("２０２６-01-05", id="fullwidth-digits"),
    pytest.param(sentinels.CLIENT_SECRET, id="text"),
]


@pytest.mark.req("AC-1")
@pytest.mark.parametrize("text", BAD_DATES)
def test_a_malformed_start_gets_the_format_sentence_and_no_echo(text: str) -> None:
    result = check(start=text)

    assert (result.errors, result.warnings, result.request) == ((START_FORMAT,), (), None)


@pytest.mark.req("AC-1")
@pytest.mark.parametrize("text", BAD_DATES)
def test_a_malformed_end_gets_the_format_sentence_and_no_echo(text: str) -> None:
    result = check(end=text)

    assert (result.errors, result.warnings, result.request) == ((END_FORMAT,), (), None)


@pytest.mark.req("AC-1")
def test_a_lone_start_reports_the_missing_end_with_the_same_sentence() -> None:
    assert check(end=None).errors == (END_FORMAT,)


@pytest.mark.req("AC-1")
def test_a_lone_end_reports_the_missing_start_with_the_same_sentence() -> None:
    assert check(start=None).errors == (START_FORMAT,)


@pytest.mark.req("AC-1")
def test_both_dates_missing_report_both_in_order() -> None:
    assert check(start=None, end=None).errors == (START_FORMAT, END_FORMAT)


@pytest.mark.parametrize("text", ["2026-01-01", "2028-02-29", "1970-01-01", "9999-12-31"])
def test_strict_iso_dates_parse(text: str) -> None:
    assert parse_iso_date(text) == date.fromisoformat(text)


@pytest.mark.parametrize("text", [case.values[0] for case in BAD_DATES])
def test_anything_but_a_real_ascii_iso_date_does_not_parse(text: str) -> None:
    assert parse_iso_date(text) is None


# ----------------------------------------------------------------------------------- AC-9
@pytest.mark.req("AC-9")
@pytest.mark.parametrize(
    ("day", "accepted"),
    [
        pytest.param("0001-01-01", False, id="year-one"),
        pytest.param("1900-01-01", False, id="1900"),
        pytest.param("1960-01-01", False, id="1960"),
        pytest.param("1969-12-31", False, id="day-before-the-epoch"),
        pytest.param("1970-01-01", False, id="epoch-day-one-below-the-floor"),
        pytest.param("1970-01-02", True, id="the-floor"),
        pytest.param("1970-01-03", True, id="one-above-the-floor"),
        pytest.param("9999-12-29", True, id="one-below-the-ceiling"),
        pytest.param("9999-12-30", True, id="the-ceiling"),
        pytest.param("9999-12-31", False, id="one-above-the-ceiling"),
    ],
)
def test_each_date_must_lie_from_1970_01_02_to_9999_12_30(day: str, accepted: bool) -> None:
    # The other date is a day that is valid on its own and on the right side of this one.
    as_start = check(start=day, end="9999-12-30")
    as_end = check(start="1970-01-02", end=day)

    assert (as_start.errors == (), as_end.errors == ()) == (accepted, accepted)
    if not accepted:
        assert as_start.errors == (START_BOUNDS,)
        assert as_end.errors == (END_BOUNDS,)


@pytest.mark.req("AC-9", "AC-5")
def test_both_dates_out_of_bounds_print_both_lines_and_skip_the_order_check() -> None:
    # 1960 is after 1950, so a reversed-range line would be wrong; a skipped check is the point.
    assert check("1960-01-01", "1950-01-01").errors == (START_BOUNDS, END_BOUNDS)
    assert check("9999-12-31", "9999-12-31").errors == (START_BOUNDS, END_BOUNDS)


@pytest.mark.req("AC-9", "AC-5")
def test_a_date_that_fails_a_check_skips_the_order_check_whatever_it_failed() -> None:
    # Start 2027 is later than end 1960, but end is outside the bounds: one line, for end.
    assert check("2027-01-01", "1960-01-01").errors == (END_BOUNDS,)
    # Start is malformed: the end alone is judged.
    assert check("2027-1-1", "2026-01-01").errors == (START_FORMAT,)
    # End is malformed.
    assert check("2027-01-01", "2026-1-1").errors == (END_FORMAT,)
    # The bounds line is not the only way to skip: a missing date too.
    assert check(None, "2026-01-01").errors == (START_FORMAT,)


@pytest.mark.req("AC-9")
def test_the_bounds_sentence_is_the_same_in_every_zone() -> None:
    results = {
        zone: check("1970-01-01", "2026-12-31", zone).errors
        for zone in sorted(available_timezones())
    }

    assert set(results.values()) == {(START_BOUNDS,)}


@pytest.mark.req("AC-9")
def test_every_zone_accepts_the_floor_and_the_ceiling_and_builds_a_non_negative_query() -> None:
    """The sweep of PGD-16 AC-9: no zone gives a negative bound, none raises (tzdata may change)."""
    problems: list[str] = []
    zones = sorted(available_timezones())
    for zone_name in zones:
        for day in ("1970-01-02", "9999-12-30"):
            result = check(day, day, zone_name)
            request = result.request
            if request is None:
                problems.append(f"{zone_name} {day}: {result.errors}")
                continue
            zone = ZoneInfo(zone_name)
            try:
                query = baseline_query(DateRange.from_days(request.start, request.end, zone))
            except (ValueError, OverflowError, OSError) as exc:
                problems.append(f"{zone_name} {day}: {type(exc).__name__}")
                continue
            match = re.fullmatch(r"has:attachment filename:pdf after:(\d+) before:(\d+)", query)
            if match is None or int(match[1]) < 0 or int(match[2]) <= int(match[1]):
                problems.append(f"{zone_name} {day}: {query}")
    assert len(zones) > 400  # the sweep really ran over the zone database
    assert problems == []


# ----------------------------------------------------------------------------------- AC-2
@pytest.mark.req("AC-2")
def test_a_reversed_range_is_rejected_with_the_two_parsed_dates_in_the_sentence() -> None:
    result = check("2026-03-31", "2026-01-01")

    assert result.errors == (
        "Start date must be on or before the end date. (--start 2026-03-31 --end 2026-01-01)",
    )
    assert result.request is None


@pytest.mark.req("AC-2")
def test_the_reversed_range_sentence_never_echoes_anything_but_the_two_dates() -> None:
    result = check(sentinels.CLIENT_SECRET, "2026-01-01")

    assert sentinels.leaked(" ".join(result.errors)) == []


# ----------------------------------------------------------------------------------- AC-4
@pytest.mark.req("AC-4")
@pytest.mark.parametrize(
    "zone",
    [
        pytest.param("Mars/Olympus", id="unknown"),
        pytest.param("IST", id="abbreviation"),
        pytest.param("", id="empty"),
        pytest.param("Asia/Kolkata ", id="trailing-space"),
        pytest.param(" Asia/Kolkata", id="leading-space"),
        pytest.param("Asia\\Kolkata", id="backslash"),
        pytest.param("utc", id="lower-case-utc"),
        pytest.param("asia/kolkata", id="lower-case-kolkata"),
        pytest.param("ASIA/KOLKATA", id="upper-case-kolkata"),
        pytest.param("../etc/passwd", id="path-traversal"),
        pytest.param("America", id="a-directory"),
        pytest.param("Asia/Kolkata\x00", id="nul-byte"),
        pytest.param(f"Zone/{sentinels.CLIENT_SECRET}", id="sentinel"),
        pytest.param(None, id="system-zone-unresolved"),
    ],
)
def test_a_name_outside_the_iana_set_is_rejected_as_written_with_no_echo(zone: str | None) -> None:
    result = check(zone=zone)

    assert (result.errors, result.warnings, result.request) == ((ZONE_ERROR,), (), None)


@pytest.mark.req("AC-4")
@pytest.mark.parametrize("zone", ["UTC", "Asia/Kolkata", "America/New_York", "Etc/GMT-14"])
def test_a_name_in_the_iana_set_is_accepted(zone: str) -> None:
    result = check(zone=zone)

    assert result.errors == ()
    assert result.request == RunRequest(date(2026, 1, 1), date(2026, 1, 31), zone)


# ----------------------------------------------------------------------------------- AC-5
@pytest.mark.req("AC-5")
def test_every_error_is_reported_in_the_order_start_end_range_zone() -> None:
    assert check("2026-1-5", "2026-01-31", "Mars/Olympus").errors == (START_FORMAT, ZONE_ERROR)
    assert check("2026-1-5", "x", "Mars/Olympus").errors == (START_FORMAT, END_FORMAT, ZONE_ERROR)
    assert check("1960-01-01", "2026-1-5", "").errors == (START_BOUNDS, END_FORMAT, ZONE_ERROR)
    assert check("2026-03-31", "2026-01-01", "Mars/Olympus").errors == (
        "Start date must be on or before the end date. (--start 2026-03-31 --end 2026-01-01)",
        ZONE_ERROR,
    )


@pytest.mark.req("AC-5", "AC-9")
def test_a_bounds_line_and_a_zone_line_come_in_that_order() -> None:
    assert check("1970-01-01", "2026-01-01", "Mars/Olympus").errors == (START_BOUNDS, ZONE_ERROR)


# ----------------------------------------------------------------------------------- AC-3
@pytest.mark.req("AC-3")
@pytest.mark.parametrize(
    ("zone", "end", "warned"),
    [
        pytest.param("UTC", "2026-01-14", False, id="utc-yesterday"),
        pytest.param("UTC", "2026-01-15", False, id="utc-today"),
        pytest.param("UTC", "2026-01-16", True, id="utc-tomorrow"),
        pytest.param("Pacific/Kiritimati", "2026-01-16", False, id="kiritimati-today"),
        pytest.param("Pacific/Kiritimati", "2026-01-17", True, id="kiritimati-tomorrow"),
        pytest.param("Pacific/Pago_Pago", "2026-01-14", False, id="pago-pago-today"),
        pytest.param("Pacific/Pago_Pago", "2026-01-15", True, id="pago-pago-tomorrow"),
    ],
)
def test_the_end_date_is_compared_with_today_in_the_chosen_zone(
    zone: str, end: str, warned: bool
) -> None:
    result = check("2026-01-01", end, zone)

    assert result.errors == ()
    assert result.warnings == ((FUTURE_END,) if warned else ())


@pytest.mark.req("AC-3")
def test_the_clock_is_asked_for_today_in_the_chosen_zone() -> None:
    asked: list[str] = []

    def today(zone: tzinfo) -> date:
        asked.append(getattr(zone, "key", "?"))
        return date(2026, 1, 15)

    validate(raw(zone="Asia/Kolkata"), today)

    assert asked == ["Asia/Kolkata"]


@pytest.mark.req("AC-3")
@pytest.mark.parametrize(
    ("start", "end", "zone"),
    [
        pytest.param("2026-01-01", "2030-01-01", "Mars/Olympus", id="bad-zone"),
        pytest.param("2026-1-1", "2030-01-01", "UTC", id="bad-start"),
        pytest.param("2026-01-01", "2030-1-1", "UTC", id="bad-end"),
        pytest.param("2031-01-01", "2030-01-01", "UTC", id="reversed"),
        pytest.param("2026-01-01", "9999-12-31", "UTC", id="end-above-the-ceiling"),
    ],
)
def test_the_future_check_is_skipped_when_anything_is_invalid(
    start: str, end: str, zone: str
) -> None:
    def today(zone: tzinfo) -> date:
        raise AssertionError("the clock must not be read for invalid input")

    result = validate(raw(start, end, zone), today)

    assert result.errors != ()
    assert result.warnings == ()


@pytest.mark.req("AC-3", "AC-9")
def test_the_ceiling_date_is_valid_and_in_the_future() -> None:
    result = check("1970-01-02", "9999-12-30", "Etc/GMT-14")

    assert (result.errors, result.warnings) == ((), (FUTURE_END,))


# ----------------------------------------------------------------------------------- AC-7
@pytest.mark.req("AC-7")
def test_the_names_in_the_sentences_come_from_the_caller() -> None:
    names = FieldNames(start="Start", end="End", tz="Zone")

    result = validate(RawInput("x", "y", "z", names), CLOCK.today)

    assert result.errors == (
        "Start: Enter the date as YYYY-MM-DD, for example 2026-01-31.",
        "End: Enter the date as YYYY-MM-DD, for example 2026-01-31.",
        "Zone: Unknown time zone. Use an IANA name such as Asia/Kolkata.",
    )


@pytest.mark.req("AC-7")
def test_the_cli_names_are_its_flag_constants() -> None:
    assert (args.FLAG_START, args.FLAG_END, args.FLAG_TZ) == ("--start", "--end", "--tz")
    assert args.FIELD_NAMES == NAMES


@pytest.mark.req("AC-7")
@pytest.mark.parametrize(
    "name",
    [
        "DATE_FORMAT_TEMPLATE",
        "DATES_REQUIRED_TOGETHER",
        "END_BEFORE_START",
        "DATE_OUT_OF_RANGE",
        "ZONE_UNKNOWN",
        "SYSTEM_ZONE_UNAVAILABLE",
    ],
)
def test_the_six_interim_rejection_constants_no_longer_exist(name: str) -> None:
    assert not hasattr(messages, name)


def _string_constants(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


@pytest.mark.req("AC-7")
def test_the_message_table_holds_no_flag_name() -> None:
    constants = _string_constants(REPO_ROOT / "gmail_pdf" / "domain" / "messages.py")

    for flag in ("--start", "--end", "--tz"):
        assert [text for text in constants if flag in text] == []


# Fragments of every sentence this story owns, old and new. None may appear in a module that is
# not the table: a front end builds no sentence of its own (FR-064).
SENTENCE_FRAGMENTS = [
    "Enter the date as",
    "Enter a date from",
    "must be on or before",
    "Unknown time zone",
    "End date is in the future",
    "must be a date written as",
    "must be given together",
    "must not be before",
    "outside the range this program",
    "not a known IANA",
    "could not be determined",
]
SOURCES_WITHOUT_SENTENCES = [
    *sorted((REPO_ROOT / "gmail_pdf" / "cli").glob("*.py")),
    REPO_ROOT / "gmail_pdf" / "domain" / "daterange.py",
    REPO_ROOT / "gmail_pdf" / "infra" / "tz.py",
    REPO_ROOT / "gmail_pdf" / "app" / "runner.py",
]


@pytest.mark.req("AC-7")
@pytest.mark.parametrize("path", SOURCES_WITHOUT_SENTENCES, ids=lambda path: path.name)
def test_no_rejection_sentence_is_written_outside_the_message_table(path: Path) -> None:
    constants = _string_constants(path)

    assert [text for text in constants for part in SENTENCE_FRAGMENTS if part in text] == []


@pytest.mark.req("AC-7")
@pytest.mark.parametrize(
    "path",
    [
        REPO_ROOT / "gmail_pdf" / "cli" / "args.py",
        REPO_ROOT / "gmail_pdf" / "domain" / "daterange.py",
        REPO_ROOT / "gmail_pdf" / "infra" / "tz.py",
    ],
    ids=lambda path: path.name,
)
def test_these_modules_import_neither_the_message_table_nor_the_input_error(path: Path) -> None:
    imported = {
        alias.name
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert imported.isdisjoint({"messages", "InputValidationError"})
