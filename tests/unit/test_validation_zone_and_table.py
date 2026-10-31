"""PGD-16 AC-3, AC-4, AC-5 and AC-7: the zone, the future-end warning and the message table.

The two dates and their bounds are in ``tests/unit/test_validation.py``. Every expected sentence
is a literal (see ``tests/support/validation_inputs.py``), never read back from
``domain/messages.py``, so a changed sentence fails here. "Today" comes from a clock frozen at one
instant: nothing depends on the machine's date or zone.
"""

from __future__ import annotations

import ast
from datetime import date, tzinfo
from pathlib import Path

import pytest

from gmail_pdf.cli import args
from gmail_pdf.domain import messages
from gmail_pdf.domain.models import RunRequest
from gmail_pdf.domain.validation import (
    FieldNames,
    RawInput,
    validate,
)
from tests.support import sentinels
from tests.support.subprocess_env import REPO_ROOT
from tests.support.validation_inputs import (
    CLOCK,
    END_FORMAT,
    FUTURE_END,
    NAMES,
    START_BOUNDS,
    START_FORMAT,
    ZONE_ERROR,
    check,
    raw,
)

pytestmark = pytest.mark.req("FR-015", "NFR-024")


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
def test_these_modules_do_not_import_the_message_table(path: Path) -> None:
    imported = {
        alias.name
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert "messages" not in imported


@pytest.mark.req("AC-7")
def test_only_validation_builds_a_run_request() -> None:
    builders = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "gmail_pdf").rglob("*.py")
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.Call)
        and getattr(node.func, "id", getattr(node.func, "attr", None)) == "RunRequest"
    }

    assert builders == {"gmail_pdf/domain/validation.py"}
