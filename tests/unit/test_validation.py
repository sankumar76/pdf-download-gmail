"""PGD-16 AC-1, AC-2 and AC-9: ``domain.validation`` of the two dates and their bounds.

The zone, the future-end warning and the single message table are in
``tests/unit/test_validation_zone_and_table.py``. Every expected sentence is a literal (see
``tests/support/validation_inputs.py``), never read back from ``domain/messages.py``, so a
changed sentence fails here. "Today" comes from a clock frozen at one instant: nothing depends on
the machine's date or zone.
"""

from __future__ import annotations

import re
from datetime import date
from zoneinfo import ZoneInfo, available_timezones

import pytest

from gmail_pdf.domain import validation
from gmail_pdf.domain.daterange import DateRange
from gmail_pdf.domain.models import RunRequest
from gmail_pdf.domain.query import baseline_query
from gmail_pdf.domain.validation import (
    ValidationResult,
    parse_iso_date,
)
from tests.support import sentinels
from tests.support.validation_inputs import (
    END_BOUNDS,
    END_FORMAT,
    START_BOUNDS,
    START_FORMAT,
    check,
)

pytestmark = pytest.mark.req("FR-015", "NFR-024")


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


@pytest.fixture
def lenient_date(monkeypatch: pytest.MonkeyPatch) -> None:
    """``date.fromisoformat`` is not the guard: a lenient parser is, and the pattern must hold.

    CPython's C implementation refuses Arabic-Indic digits and trailing text, but the pure-Python
    one (PyPy, or a build without ``_datetime``) reads digits with ``int()``. This stand-in reads
    the first ten characters the same way, so the regular expression is what has to refuse them.
    """

    class Lenient:
        @staticmethod
        def fromisoformat(text: str) -> date:
            year, month, day = text[:10].split("-")
            return date(int(year), int(month), int(day))

    monkeypatch.setattr(validation, "date", Lenient)


@pytest.mark.req("AC-1")
@pytest.mark.parametrize(
    "text",
    [
        pytest.param("٢٠٢٦-٠١-٠٥", id="arabic-indic-digits"),
        pytest.param("２０２６-０１-０５", id="fullwidth-digits"),
        pytest.param("2026-01-05\n", id="trailing-newline"),
        pytest.param("2026-01-05T00:00:00", id="date-time"),
    ],
)
def test_the_pattern_alone_keeps_out_other_digit_scripts_and_trailing_text(
    lenient_date: None, text: str
) -> None:
    assert validation.parse_iso_date(text) is None


@pytest.mark.req("AC-1")
def test_the_pattern_lets_a_plain_iso_date_through_even_with_a_lenient_parser(
    lenient_date: None,
) -> None:
    assert validation.parse_iso_date("2026-01-05") == date(2026, 1, 5)


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
@pytest.mark.parametrize("role", ["start", "end"])
def test_each_date_must_lie_from_1970_01_02_to_9999_12_30(
    day: str, accepted: bool, role: str
) -> None:
    # The other date is a day that is valid on its own and on the right side of this one.
    result = check(start=day, end="9999-12-30") if role == "start" else check("1970-01-02", day)

    rejection = (START_BOUNDS,) if role == "start" else (END_BOUNDS,)
    assert result.errors == (() if accepted else rejection)


@pytest.mark.req("AC-9", "AC-5")
@pytest.mark.parametrize(
    ("start", "end"),
    [
        # 1960 is after 1950, so a reversed-range line would be wrong; a skipped check is the point.
        pytest.param("1960-01-01", "1950-01-01", id="both-below-the-floor-in-reverse-order"),
        pytest.param("9999-12-31", "9999-12-31", id="both-above-the-ceiling"),
    ],
)
def test_both_dates_out_of_bounds_print_both_lines_and_skip_the_order_check(
    start: str, end: str
) -> None:
    assert check(start, end).errors == (START_BOUNDS, END_BOUNDS)


@pytest.mark.req("AC-9", "AC-5")
@pytest.mark.parametrize(
    ("start", "end", "errors"),
    [
        # Start 2027 is later than end 1960, but end is outside the bounds: one line, for end.
        pytest.param("2027-01-01", "1960-01-01", (END_BOUNDS,), id="end-out-of-bounds"),
        # Start is malformed: the end alone is judged.
        pytest.param("2027-1-1", "2026-01-01", (START_FORMAT,), id="start-malformed"),
        pytest.param("2027-01-01", "2026-1-1", (END_FORMAT,), id="end-malformed"),
        # The bounds line is not the only way to skip: a missing date too.
        pytest.param(None, "2026-01-01", (START_FORMAT,), id="start-missing"),
    ],
)
def test_a_date_that_fails_a_check_skips_the_order_check_whatever_it_failed(
    start: str | None, end: str, errors: tuple[str, ...]
) -> None:
    assert check(start, end).errors == errors


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
