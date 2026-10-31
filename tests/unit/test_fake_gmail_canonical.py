"""AC-7: canonical mailboxes (RD 4.4 table, boundary, DST) and JSON persistence."""

from __future__ import annotations

import copy
import random
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


def _listed(overrides: dict[str, object]) -> dict[str, object]:
    """A message entry with a valid resource, with some resource keys replaced."""
    resource: dict[str, object] = {"id": "m1", "internalDate": "1700000000000", "payload": {}}
    resource.update(overrides)
    return {"resource": resource, "attachments": {}}


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
        pytest.param(
            {"format": 1, "messages": [_listed({"payload": None})]},
            id="payload-null",
        ),
        pytest.param(
            {"format": 1, "messages": [_listed({"payload": "text"})]},
            id="payload-not-an-object",
        ),
        pytest.param(
            {"format": 1, "messages": [_listed({"internalDate": None})]},
            id="internal-date-null",
        ),
        pytest.param(
            {"format": 1, "messages": [_listed({"internalDate": 1700000000000})]},
            id="internal-date-not-a-string",
        ),
        pytest.param(
            {"format": 1, "messages": [_listed({"internalDate": "²"})]},
            id="internal-date-superscript-digit",
        ),
        pytest.param(
            {"format": 1, "messages": [_listed({"internalDate": ""})]},
            id="internal-date-empty",
        ),
    ],
)
def test_malformed_json_documents_are_rejected(document: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        from_json_dict(document)


@pytest.mark.req("DEF-001", "issue-15")
def test_a_resource_without_payload_or_internal_date_is_rejected_at_load_not_at_listing() -> None:
    document = {"format": 1, "messages": [{"resource": {"id": "a"}, "attachments": {}}]}

    with pytest.raises(ValueError, match="payload"):
        from_json_dict(document)


def test_json_file_must_hold_an_object(tmp_path: Path) -> None:
    path = tmp_path / "list.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="object"):
        load_fake_gmail_from_json_file(path)


# ------------------------------------------------------------ QUA-39: the load does the checking
def _nested_lists(levels: int) -> object:
    """``levels`` arrays inside one another, innermost empty."""
    value: object = []
    for _ in range(levels - 1):
        value = [value]
    return value


def _part_chain(depth: int) -> dict[str, object]:
    """A ``payload`` whose ``parts`` nest ``depth`` levels deep."""
    node: dict[str, object] = {}
    for _ in range(depth):
        node = {"parts": [node]}
    return node


def _doc(overrides: dict[str, object], **settings: object) -> dict[str, object]:
    return {"format": 1, "messages": [_listed(overrides)], **settings}


def _read_everything(fake: FakeGmail) -> None:
    """Every read the run makes: the baseline listing and one ``get_message`` per message."""
    list_all(fake, BASELINE_QUERY)
    for message_id in fake.message_ids:
        fake.get_message(message_id)


def _payload(**keys: object) -> dict[str, object]:
    return {"payload": keys}


REJECTED_AT_LOAD: dict[str, dict[str, object]] = {
    "parts-of-numbers": _doc(_payload(parts=[5])),
    "parts-of-null": _doc(_payload(parts=[None])),
    "parts-of-strings": _doc(_payload(parts=["x"])),
    "parts-not-a-list": _doc(_payload(parts=5)),
    "nested-parts-of-numbers": _doc(_payload(parts=[{"parts": [5]}])),
    "label-ids-number": _doc({"labelIds": 5}),
    "label-ids-null": _doc({"labelIds": None}),
    "label-ids-unhashable": _doc({"labelIds": [[]]}),
    "label-ids-numbers": _doc({"labelIds": [5]}),
    "label-ids-string": _doc({"labelIds": "SPAM"}),
    "headers-number": _doc(_payload(headers=5)),
    "headers-null": _doc(_payload(headers=None)),
    "headers-of-strings": _doc(_payload(headers=["x"])),
    "internal-date-5000-digits": _doc({"internalDate": "1" * 5000}),
    "internal-date-21-digits": _doc({"internalDate": "1" * 21}),
    "latency-inf-text": _doc({}, latency_s="inf"),
    "latency-1e300": _doc({}, latency_s=1e300),
    "latency-nan": _doc({}, latency_s="nan"),
    "latency-negative": _doc({}, latency_s=-1),
    "latency-over-an-hour": _doc({}, latency_s=3601),
    "parts-depth-247": _doc({"payload": _part_chain(247)}),
    "parts-depth-1400": _doc({"payload": _part_chain(1400)}),
    "resource-depth-500": _doc({"unread": _nested_lists(500)}),
    "resource-depth-2900": _doc({"unread": _nested_lists(2900)}),
    "unread-key-depth-2900": {"format": 1, "messages": [], "unread": _nested_lists(2900)},
}


@pytest.mark.req("AC-6", "QUA-39")
@pytest.mark.parametrize("document", REJECTED_AT_LOAD.values(), ids=REJECTED_AT_LOAD.keys())
def test_content_a_later_read_would_choke_on_is_rejected_at_load(
    document: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        from_json_dict(document)


@pytest.mark.req("AC-6", "QUA-39")
def test_the_depth_cap_is_199_levels_under_a_top_level_key_and_200_is_refused() -> None:
    # Literals, not the module constant: the test must not follow a change of the cap.
    from_json_dict({"format": 1, "messages": [], "unread": _nested_lists(199)})

    with pytest.raises(ValueError, match="nested"):
        from_json_dict({"format": 1, "messages": [], "unread": _nested_lists(200)})


@pytest.mark.req("AC-6", "QUA-39")
def test_ordinary_variants_still_load_and_read() -> None:
    chain = _part_chain(90)  # well under the cap
    chain["headers"] = [{"name": "Subject", "value": "x"}]
    document = _doc(
        {"labelIds": [], "payload": chain, "unknownKey": {"anything": [1, None, "text", 1.5]}},
        latency_s=0.0,
        unknown_top_level_key=[{"a": 1}],
    )

    _read_everything(from_json_dict(document))


# Hostile values and places; the property below mixes them at random with a fixed seed.
HOSTILE_VALUES: list[object] = [None, 5, -1, 1.5, "x", "", "inf", "9" * 30, True, [], {}, [None]]
HOSTILE_VALUES += [[5], ["x"], [[]], [{}], {"a": []}, _nested_lists(150), _nested_lists(250)]
HOSTILE_PLACES = [("labelIds",), ("internalDate",), ("payload",), ("payload", "parts"), ("id",)]
HOSTILE_PLACES += [("payload", "headers"), ("payload", "filename"), ("payload", "body")]
HOSTILE_SETTINGS = ["latency_s", "page_size", "shuffle_seed", "epoch_bounds"]


def _hostile_document(rng: random.Random) -> dict[str, object]:
    """A valid one-message document with one to three hostile values put in random places."""
    resource: dict[str, object] = {
        "id": "m1",
        "internalDate": "1700000000000",
        "payload": {"parts": [{"filename": "a.pdf"}], "headers": []},
    }
    for _ in range(rng.randint(1, 3)):
        *path, leaf = rng.choice(HOSTILE_PLACES)
        target: object = resource
        for key in path:
            target = target.get(key) if isinstance(target, dict) else None
        if isinstance(target, dict):
            target[leaf] = copy.deepcopy(rng.choice(HOSTILE_VALUES))
    document: dict[str, object] = {
        "format": 1,
        "messages": [{"resource": resource, "attachments": {}}],
    }
    if rng.random() < 0.3:
        document[rng.choice(HOSTILE_SETTINGS)] = copy.deepcopy(rng.choice(HOSTILE_VALUES))
    return document


@pytest.mark.req("AC-6", "QUA-39")
def test_any_content_is_rejected_at_load_or_read_without_an_exception() -> None:
    """The property behind AC-6 (iii): a loaded document never fails in a later read."""
    rng = random.Random(39)
    accepted = rejected = 0
    for _ in range(600):
        try:
            fake = from_json_dict(_hostile_document(rng))
        except ValueError:
            rejected += 1
            continue
        fake.latency_s = 0.0  # an accepted latency is a real sleep; the reads are the point
        _read_everything(fake)
        accepted += 1
    assert accepted > 20
    assert rejected > 20
