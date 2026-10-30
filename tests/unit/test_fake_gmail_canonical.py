"""AC-7: canonical mailboxes (RD 4.4 table, boundary, DST) and JSON persistence."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.fakes.fake_gmail import EpochBounds, FakeGmail
from tests.fakes.fake_gmail_json import (
    dump_fake_gmail_to_json_file,
    from_json_dict,
    load_fake_gmail_from_json_file,
)
from tests.fixtures.canonical import RangeCase, boundary_cases, dst_cases, rd_example_table
from tests.fixtures.helpers import BASELINE_QUERY, day_bounds, list_all

pytestmark = pytest.mark.req("NFR-022", "AC-7")

ALL_CASES = [*boundary_cases(), *dst_cases()]
IN_RANGE_CASES = [case for case in ALL_CASES if case.in_range]


def _case_id(case: RangeCase) -> str:
    return f"{case.day}-{case.label}"


def _internal_seconds(case: RangeCase) -> int:
    return int(case.message.resource["internalDate"]) // 1000


def _hit(case: RangeCase, bounds: EpochBounds, query: str) -> bool:
    return bool(list_all(FakeGmail([case.message], epoch_bounds=bounds), query))


# ------------------------------------------------------------------ RD 4.4 table
def test_rd_example_table_has_the_six_documented_saved_names() -> None:
    assert [row.expected_saved_name for row in rd_example_table()] == [
        "20260115_Invoice.pdf",
        "20260115_Invoice_1.pdf",
        "20260115_invoice_2.pdf",
        "20260116_Invoice.pdf",
        "20260120_Report_Q4.pdf",
        "20260121_attachment.pdf",
    ]


def test_baseline_filename_search_misses_the_nameless_pdf() -> None:
    # Like Gmail, the baseline filename search cannot see a PDF without a name.
    fake = FakeGmail([row.message for row in rd_example_table()])

    assert len(list_all(fake)) == 5


def test_sweep_query_finds_only_the_nameless_pdf() -> None:
    fake = FakeGmail([row.message for row in rd_example_table()])

    assert list_all(fake, "has:attachment -filename:pdf") == ["m-0121"]


def test_nameless_pdf_part_has_an_empty_filename_and_pdf_mime_type() -> None:
    fake = FakeGmail([row.message for row in rd_example_table()])

    part = fake.get_message("m-0121")["payload"]["parts"][0]

    assert (part["filename"], part["mimeType"]) == ("", "application/pdf")


# ------------------------------------------------------------------ boundary and DST sets
@pytest.mark.parametrize("case", ALL_CASES, ids=_case_id)
def test_fixture_label_matches_the_exact_local_day_range(case: RangeCase) -> None:
    start, end = day_bounds(case.day, case.tz)

    assert (start <= _internal_seconds(case) < end) is case.in_range


@pytest.mark.parametrize("bounds", list(EpochBounds), ids=lambda b: b.value)
@pytest.mark.parametrize("case", ALL_CASES, ids=_case_id)
def test_unwidened_query_result_is_specific_to_the_epoch_interpretation(
    case: RangeCase, bounds: EpochBounds
) -> None:
    start, end = day_bounds(case.day, case.tz)
    seconds = _internal_seconds(case)
    expected = start <= seconds <= end if bounds is EpochBounds.INCLUSIVE else start < seconds < end

    assert _hit(case, bounds, f"{BASELINE_QUERY} after:{start} before:{end}") is expected


@pytest.mark.parametrize("bounds", list(EpochBounds), ids=lambda b: b.value)
@pytest.mark.parametrize("case", ALL_CASES, ids=_case_id)
def test_widened_query_result_is_specific_to_the_epoch_interpretation(
    case: RangeCase, bounds: EpochBounds
) -> None:
    start, end = day_bounds(case.day, case.tz)
    low, high = start - 1, end + 1
    seconds = _internal_seconds(case)
    expected = low <= seconds <= high if bounds is EpochBounds.INCLUSIVE else low < seconds < high

    assert _hit(case, bounds, f"{BASELINE_QUERY} after:{low} before:{high}") is expected


@pytest.mark.parametrize("bounds", list(EpochBounds), ids=lambda b: b.value)
@pytest.mark.parametrize("case", IN_RANGE_CASES, ids=_case_id)
def test_widened_query_never_loses_an_in_range_message(
    case: RangeCase, bounds: EpochBounds
) -> None:
    start, end = day_bounds(case.day, case.tz)

    assert _hit(case, bounds, f"{BASELINE_QUERY} after:{start - 1} before:{end + 1}")


def test_dst_days_have_23_and_25_hours() -> None:
    spring = day_bounds("2026-03-08", "America/New_York")
    fall = day_bounds("2026-11-01", "America/New_York")

    assert ((spring[1] - spring[0]) // 3600, (fall[1] - fall[0]) // 3600) == (23, 25)


def test_ambiguous_fall_back_time_yields_two_instants_an_hour_apart() -> None:
    first, second = [c for c in dst_cases() if c.label.startswith("fall-01-30")]

    assert _internal_seconds(second) - _internal_seconds(first) == 3600


def test_canonical_content_uses_example_com_only() -> None:
    messages = [row.message for row in rd_example_table()] + [c.message for c in dst_cases()]
    text = " ".join(str(message.resource) for message in messages)

    assert "@example.com" in text
    assert "gmail.com" not in text


# ------------------------------------------------------------------ JSON persistence
@pytest.fixture
def round_tripped(tmp_path: Path) -> tuple[FakeGmail, FakeGmail]:
    original = FakeGmail(
        [row.message for row in rd_example_table()],
        page_size=2,
        shuffle_seed=5,
        epoch_bounds=EpochBounds.EXCLUSIVE,
    )
    path = tmp_path / "mailbox.json"
    dump_fake_gmail_to_json_file(original, path)
    return original, load_fake_gmail_from_json_file(path)


def test_json_round_trip_preserves_settings(round_tripped: tuple[FakeGmail, FakeGmail]) -> None:
    _, loaded = round_tripped

    assert (loaded.page_size, loaded.shuffle_seed, loaded.epoch_bounds) == (
        2,
        5,
        EpochBounds.EXCLUSIVE,
    )


def test_json_round_trip_preserves_messages(round_tripped: tuple[FakeGmail, FakeGmail]) -> None:
    original, loaded = round_tripped

    assert [m.resource for m in loaded.messages] == [m.resource for m in original.messages]


def test_json_round_trip_preserves_attachment_bytes(
    round_tripped: tuple[FakeGmail, FakeGmail],
) -> None:
    original, loaded = round_tripped

    assert [m.attachments for m in loaded.messages] == [m.attachments for m in original.messages]


def test_json_defaults_match_the_constructor_defaults() -> None:
    loaded = from_json_dict({"format": 1, "messages": []})

    assert (loaded.page_size, loaded.epoch_bounds) == (
        FakeGmail().page_size,
        FakeGmail().epoch_bounds,
    )


@pytest.mark.parametrize(
    "document",
    [
        pytest.param({"format": 99, "messages": []}, id="unknown-format"),
        pytest.param({"format": 1, "messages": "nope"}, id="messages-not-a-list"),
        pytest.param({"format": 1, "messages": [{"resource": {}}]}, id="missing-attachments"),
        pytest.param({"format": 1, "messages": [5]}, id="message-not-an-object"),
        pytest.param(
            {"format": 1, "messages": [{"resource": {}, "attachments": {}}]},
            id="message-without-id",
        ),
        pytest.param(
            {"format": 1, "messages": [{"resource": {"id": 7}, "attachments": {}}]},
            id="message-id-not-a-string",
        ),
    ],
)
def test_malformed_json_documents_are_rejected(document: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        from_json_dict(document)


def test_json_file_must_hold_an_object(tmp_path: Path) -> None:
    path = tmp_path / "list.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="object"):
        load_fake_gmail_from_json_file(path)
