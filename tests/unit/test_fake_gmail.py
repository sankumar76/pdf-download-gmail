"""AC-7: every FakeGmail capability has a unit test."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from gmail_pdf.app.ports import GmailPort
from tests.fakes.fake_gmail import (
    EpochBounds,
    FakeGmail,
    FakeGmailHttpError,
    FakeGmailTimeout,
    UnsupportedQueryError,
    b64url_decode,
    dump_fake_gmail_to_json_file,
    iter_parts,
    load_fake_gmail_from_json_file,
)
from tests.fixtures.builders import MessageBuilder, build_messages, epoch_ms
from tests.fixtures.canonical import boundary_cases, dst_cases, rd_example_table

pytestmark = pytest.mark.req("NFR-022", "AC-7")

BASELINE_QUERY = "has:attachment filename:pdf"


def numbered_mailbox(count: int, **kwargs: object) -> FakeGmail:
    """`count` PDF messages received one hour apart (m01 oldest)."""
    builders = [
        MessageBuilder(f"m{index:02d}").received(f"2026-01-15T{index:02d}:00:00").pdf("a.pdf")
        for index in range(count)
    ]
    return FakeGmail(build_messages(builders), **kwargs)  # type: ignore[arg-type]


def list_all(fake: GmailPort, query: str = BASELINE_QUERY) -> list[str]:
    ids: list[str] = []
    token: str | None = None
    while True:
        page = fake.list_message_ids(query, page_token=token)
        ids.extend(page.message_ids)
        token = page.next_page_token
        if token is None:
            return ids


def day_bounds(day: str, tz: str) -> tuple[int, int]:
    """Epoch seconds of local 00:00 on `day` and on the next day (independent of the fake)."""
    start = date.fromisoformat(day)
    first = epoch_ms(f"{start}T00:00:00", tz) // 1000
    last = epoch_ms(f"{start + timedelta(days=1)}T00:00:00", tz) // 1000
    return first, last


# ------------------------------------------------------------------ paging and order
def test_pages_follow_the_configured_page_size() -> None:
    fake = numbered_mailbox(5, page_size=2)

    first = fake.list_message_ids(BASELINE_QUERY)
    second = fake.list_message_ids(BASELINE_QUERY, page_token=first.next_page_token)

    assert len(first.message_ids) == 2 and first.next_page_token is not None
    assert len(second.message_ids) == 2 and second.next_page_token is not None
    assert len(list_all(fake)) == 5


def test_last_page_has_no_next_token() -> None:
    page = numbered_mailbox(3, page_size=3).list_message_ids(BASELINE_QUERY)

    assert page.next_page_token is None


def test_default_order_is_newest_first() -> None:
    assert list_all(numbered_mailbox(4)) == ["m03", "m02", "m01", "m00"]


def test_shuffled_order_differs_from_default_but_is_complete_and_reproducible() -> None:
    ordered = list_all(numbered_mailbox(12))
    first = list_all(numbered_mailbox(12, shuffle_seed=7))
    again = list_all(numbered_mailbox(12, shuffle_seed=7))

    assert first != ordered
    assert sorted(first) == sorted(ordered)
    assert first == again


def test_shuffle_changes_between_list_calls_on_one_fake() -> None:
    fake = numbered_mailbox(12, shuffle_seed=7)

    assert list_all(fake) != list_all(fake)


def test_paging_is_stable_within_one_shuffled_listing() -> None:
    fake = numbered_mailbox(9, page_size=4, shuffle_seed=3)

    ids = list_all(fake)

    assert len(ids) == len(set(ids)) == 9


def test_unknown_page_token_is_http_400() -> None:
    with pytest.raises(FakeGmailHttpError) as exc_info:
        numbered_mailbox(1).list_message_ids(BASELINE_QUERY, page_token="bogus")

    assert exc_info.value.status == 400


def test_page_size_must_be_positive() -> None:
    with pytest.raises(ValueError, match="page_size"):
        FakeGmail(page_size=0)


def test_duplicate_message_id_is_rejected() -> None:
    message = MessageBuilder("dup").pdf("a.pdf").build()

    with pytest.raises(ValueError, match="duplicate"):
        FakeGmail([message, message])


# ------------------------------------------------------------------ query terms
def test_has_attachment_and_filename_terms() -> None:
    fake = FakeGmail(
        build_messages(
            [
                MessageBuilder("with-pdf").pdf("a.pdf"),
                MessageBuilder("with-png").attachment("a.png", "image/png", b"x"),
                MessageBuilder("text-only").text(),
                MessageBuilder("upper").pdf("B.PDF"),
            ]
        )
    )

    assert sorted(list_all(fake, "has:attachment")) == ["upper", "with-pdf", "with-png"]
    assert sorted(list_all(fake, "filename:pdf")) == ["upper", "with-pdf"]
    assert list_all(fake, "has:attachment -filename:pdf") == ["with-png"]


def test_plain_words_match_the_subject_and_unknown_operators_are_rejected() -> None:
    fake = FakeGmail(
        build_messages([MessageBuilder("a").subject("Quarterly Report"), MessageBuilder("b")])
    )

    assert list_all(fake, "quarterly") == ["a"]
    with pytest.raises(UnsupportedQueryError):
        list_all(fake, "label:inbox")


def test_spam_and_trash_are_excluded_unless_requested() -> None:
    fake = FakeGmail(
        build_messages(
            [MessageBuilder("ok").pdf("a.pdf"), MessageBuilder("bad").pdf("a.pdf").labels("SPAM")]
        )
    )

    assert list_all(fake) == ["ok"]
    assert sorted(fake.list_message_ids(BASELINE_QUERY, include_spam_trash=True).message_ids) == [
        "bad",
        "ok",
    ]


# ------------------------------------------------------------------ epoch interpretation
@pytest.mark.parametrize(
    ("bounds", "after_hit", "before_hit"),
    [(EpochBounds.INCLUSIVE, True, True), (EpochBounds.EXCLUSIVE, False, False)],
)
def test_epoch_terms_follow_the_switchable_interpretation(
    bounds: EpochBounds, after_hit: bool, before_hit: bool
) -> None:
    second = epoch_ms("2026-01-15T00:00:00") // 1000
    fake = FakeGmail(
        build_messages([MessageBuilder("edge").received("2026-01-15T00:00:00").pdf("a.pdf")]),
        epoch_bounds=bounds,
    )

    assert bool(list_all(fake, f"after:{second}")) is after_hit
    assert bool(list_all(fake, f"before:{second}")) is before_hit


def test_epoch_interpretation_can_be_switched_on_a_live_fake() -> None:
    second = epoch_ms("2026-01-15T00:00:00") // 1000
    fake = FakeGmail(
        build_messages([MessageBuilder("edge").received("2026-01-15T00:00:00").pdf("a.pdf")])
    )

    assert list_all(fake, f"after:{second}") == ["edge"]
    fake.epoch_bounds = EpochBounds.EXCLUSIVE
    assert list_all(fake, f"after:{second}") == []


# ------------------------------------------------------------------ messages and attachments
def test_get_message_returns_an_independent_copy() -> None:
    fake = FakeGmail([MessageBuilder("m1").pdf("a.pdf").build()])

    first = fake.get_message("m1")
    first["payload"]["parts"].clear()

    assert fake.get_message("m1")["payload"]["parts"]


def test_get_message_unknown_id_is_http_404() -> None:
    with pytest.raises(FakeGmailHttpError) as exc_info:
        FakeGmail().get_message("missing")

    assert exc_info.value.status == 404


def test_nested_multipart_and_forwarded_message_parts_are_reachable() -> None:
    inner = MessageBuilder().subject("inner").pdf("inner.pdf")
    message = MessageBuilder("m1").text()
    with message.multipart("related"), message.multipart("alternative"):
        message.pdf("deep.pdf")
    message.forwarded(inner)
    fake = FakeGmail([message.build()])

    parts = list(iter_parts(fake.get_message("m1")["payload"]))

    by_name = {part["filename"]: part for part in parts if part["filename"]}
    assert set(by_name) == {"deep.pdf", "inner.pdf"}
    assert by_name["deep.pdf"]["partId"] == "1.0.0"
    assert by_name["inner.pdf"]["partId"].count(".") >= 2
    assert "message/rfc822" in {part["mimeType"] for part in parts}
    assert {"multipart/related", "multipart/alternative"} <= {part["mimeType"] for part in parts}


def test_attachment_id_body_is_served_by_get_attachment_and_inline_body_is_not() -> None:
    content = b"%PDF-1.4 distinctive"
    message = (
        MessageBuilder("m1")
        .pdf("big.pdf", content=content)
        .pdf("small.pdf", content=b"abc", inline=True)
    )
    fake = FakeGmail([message.build()])

    parts = {
        p["filename"]: p for p in iter_parts(fake.get_message("m1")["payload"]) if p["filename"]
    }
    big, small = parts["big.pdf"]["body"], parts["small.pdf"]["body"]

    assert "data" not in big and fake.get_attachment("m1", big["attachmentId"]) == content
    assert "attachmentId" not in small and b64url_decode(small["data"]) == b"abc"


def test_get_attachment_unknown_ids_are_http_404() -> None:
    fake = FakeGmail([MessageBuilder("m1").pdf("a.pdf").build()])

    for message_id, attachment_id in [("m1", "nope"), ("missing", "att-m1-1")]:
        with pytest.raises(FakeGmailHttpError) as exc_info:
            fake.get_attachment(message_id, attachment_id)
        assert exc_info.value.status == 404


# ------------------------------------------------------------------ faults, latency, recorder
@pytest.mark.parametrize(
    ("status", "reason"),
    [
        (429, "rateLimitExceeded"),
        (500, ""),
        (503, "backendError"),
        (403, "rateLimitExceeded"),
        (400, ""),
        (404, ""),
    ],
)
def test_scripted_http_faults_fire_once_then_the_call_succeeds(status: int, reason: str) -> None:
    fake = FakeGmail([MessageBuilder("m1").pdf("a.pdf").build()])
    fake.fail_with_http("get_message", status, reason, retry_after=3.0)

    with pytest.raises(FakeGmailHttpError) as exc_info:
        fake.get_message("m1")

    assert (exc_info.value.status, exc_info.value.reason, exc_info.value.retry_after) == (
        status,
        reason,
        3.0,
    )
    assert fake.get_message("m1")["id"] == "m1"


def test_scripted_timeout() -> None:
    fake = FakeGmail([MessageBuilder("m1").pdf("a.pdf").build()])
    fake.fail_with_timeout("get_message")

    with pytest.raises(FakeGmailTimeout):
        fake.get_message("m1")
    assert fake.get_message("m1")["id"] == "m1"


def test_fault_skip_times_and_parameter_match() -> None:
    fake = numbered_mailbox(3)
    fake.fail_with_http("get_message", 500, times=2, skip=1, message_id="m01")

    fake.get_message("m00")  # different message: never matches
    fake.get_message("m01")  # skipped
    for _ in range(2):
        with pytest.raises(FakeGmailHttpError):
            fake.get_message("m01")
    assert fake.get_message("m01")["id"] == "m01"


def test_fault_with_unlimited_times_and_wildcard_method() -> None:
    fake = numbered_mailbox(1)
    fake.fail_with_http("*", 503, times=None)

    for _ in range(3):
        with pytest.raises(FakeGmailHttpError):
            fake.list_message_ids(BASELINE_QUERY)
    with pytest.raises(FakeGmailHttpError):
        fake.get_message("m00")


def test_latency_sleeps_before_each_call_including_faulted_ones() -> None:
    slept: list[float] = []
    fake = numbered_mailbox(1, latency_s=0.3, sleep=slept.append)
    fake.fail_with_http("get_message", 500)

    fake.list_message_ids(BASELINE_QUERY)
    with pytest.raises(FakeGmailHttpError):
        fake.get_message("m00")

    assert slept == [0.3, 0.3]


def test_no_sleep_without_latency() -> None:
    slept: list[float] = []
    numbered_mailbox(1, sleep=slept.append).list_message_ids(BASELINE_QUERY)

    assert slept == []


def test_call_recorder_keeps_method_params_and_fault_flag() -> None:
    fake = numbered_mailbox(1)
    fake.fail_with_http("get_attachment", 500)

    fake.list_message_ids(BASELINE_QUERY, include_spam_trash=True)
    fake.get_message("m00")
    attachment_id = fake.get_message("m00")["payload"]["parts"][0]["body"]["attachmentId"]
    with pytest.raises(FakeGmailHttpError):
        fake.get_attachment("m00", attachment_id)

    methods = [call.method for call in fake.calls]
    assert methods == ["list_message_ids", "get_message", "get_message", "get_attachment"]
    assert fake.calls[0].params == {
        "query": BASELINE_QUERY,
        "page_token": None,
        "include_spam_trash": True,
    }
    assert fake.calls[3].params == {"message_id": "m00", "attachment_id": attachment_id}
    assert [call.faulted for call in fake.calls] == [False, False, False, True]
    assert len(fake.calls_to("get_message")) == 2
    assert set(methods) <= {"list_message_ids", "get_message", "get_attachment"}


# ------------------------------------------------------------------ canonical sets
def test_rd_example_table_has_the_six_documented_rows() -> None:
    rows = rd_example_table()

    assert [row.expected_saved_name for row in rows] == [
        "20260115_Invoice.pdf",
        "20260115_Invoice_1.pdf",
        "20260115_invoice_2.pdf",
        "20260116_Invoice.pdf",
        "20260120_Report_Q4.pdf",
        "20260121_attachment.pdf",
    ]
    fake = FakeGmail([row.message for row in rows])
    # Like Gmail, the baseline filename search misses the nameless PDF; only the sweep finds it.
    assert len(list_all(fake)) == 5
    assert list_all(fake, "has:attachment -filename:pdf") == ["m-0121"]
    unnamed = fake.get_message("m-0121")["payload"]["parts"][0]
    assert unnamed["filename"] == "" and unnamed["mimeType"] == "application/pdf"


@pytest.mark.parametrize("bounds", list(EpochBounds))
def test_boundary_and_dst_messages_fall_in_or_out_of_the_day_range(bounds: EpochBounds) -> None:
    for case in [*boundary_cases(), *dst_cases()]:
        start, end = day_bounds(case.day, case.tz)
        internal_ms = int(case.message.resource["internalDate"])
        fake = FakeGmail([case.message], epoch_bounds=bounds)
        # The exact local range is [start, end); the query is widened by one second each side.
        widened_hit = bool(list_all(fake, f"{BASELINE_QUERY} after:{start - 1} before:{end + 1}"))

        assert (start * 1000 <= internal_ms < end * 1000) is case.in_range, case.label
        if case.in_range:
            assert widened_hit, case.label  # recall: the widened query never loses an in-range hit
        else:
            assert not widened_hit or internal_ms // 1000 in (start - 1, end), case.label


def test_dst_days_have_23_and_25_hours() -> None:
    spring = day_bounds("2026-03-08", "America/New_York")
    fall = day_bounds("2026-11-01", "America/New_York")

    assert (spring[1] - spring[0]) // 3600 == 23
    assert (fall[1] - fall[0]) // 3600 == 25


def test_ambiguous_fall_back_time_yields_two_distinct_instants() -> None:
    first, second = [c for c in dst_cases() if c.label.startswith("fall-01-30")]

    assert (
        int(second.message.resource["internalDate"]) - int(first.message.resource["internalDate"])
        == 3_600_000
    )


def test_content_is_synthetic() -> None:
    messages = [row.message for row in rd_example_table()] + [c.message for c in dst_cases()]
    for message in messages:
        text = str(message.resource)
        assert "@example.com" in text
        assert "gmail.com" not in text


# ------------------------------------------------------------------ JSON persistence
def test_json_round_trip_preserves_content_and_settings(tmp_path: Path) -> None:
    original = FakeGmail(
        [row.message for row in rd_example_table()],
        page_size=2,
        shuffle_seed=5,
        latency_s=0.0,
        epoch_bounds=EpochBounds.EXCLUSIVE,
    )
    path = tmp_path / "mailbox.json"

    dump_fake_gmail_to_json_file(original, path)
    loaded = load_fake_gmail_from_json_file(path)

    assert loaded.page_size == 2 and loaded.epoch_bounds is EpochBounds.EXCLUSIVE
    assert sorted(loaded.message_ids) == sorted(original.message_ids)
    attachment_id = original.get_message("m-0115-a")["payload"]["parts"][0]["body"]["attachmentId"]
    assert loaded.get_attachment("m-0115-a", attachment_id) == original.get_attachment(
        "m-0115-a", attachment_id
    )
    assert loaded.get_message("m-0121") == original.get_message("m-0121")


@pytest.mark.parametrize(
    "document",
    [
        {"format": 99, "messages": []},
        {"format": 1, "messages": "nope"},
        {"format": 1, "messages": [{"resource": {}}]},
        {"format": 1, "messages": [5]},
    ],
)
def test_malformed_json_documents_are_rejected(document: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        FakeGmail.from_json_dict(document)


def test_json_file_must_hold_an_object(tmp_path: Path) -> None:
    path = tmp_path / "list.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="object"):
        load_fake_gmail_from_json_file(path)
