"""STORY-03.01 AC-6 and AC-7: no PDF from a Drive link, and the body is never read (NFR-016).

AC-6 at rule level: the walker is STORY-03.02, so the message is flattened with ``iter_parts``
and each part mapped to ``PartInfo`` by a test-only helper. AC-7: the mapping runs on a
recording view of the message, so the test knows which keys were read, and every base64
decoder is replaced by a spy. The sentinel is a synthetic sentence, not a credential.
"""

from __future__ import annotations

import base64
import binascii
import email.base64mime
from collections.abc import Callable, Mapping
from dataclasses import FrozenInstanceError, fields

import pytest

from gmail_pdf.domain.mime import is_pdf_part
from gmail_pdf.domain.models import PartInfo
from tests.fakes import fake_gmail
from tests.fakes.fake_gmail import b64url_decode, b64url_encode, iter_parts
from tests.fixtures.builders import MessageBuilder
from tests.fixtures.parts import RecordingMapping, part_info, part_infos

pytestmark = pytest.mark.req("FR-019", "NFR-016")

SENTINEL_SENTENCE = "Synthetic body sentinel: the quick brown fox must stay undecoded."
DRIVE_LINK = '<a href="https://drive.google.com/file/d/SYNTHETIC-FILE-ID/view">Invoice.pdf</a>'
ALLOWED_READS = {"partId", "mimeType", "filename", "body", "parts", "size", "attachmentId"}

# Every way the standard library and the fake can turn base64 text into bytes.
DECODERS = [
    (base64, "b64decode"),
    (base64, "urlsafe_b64decode"),
    (base64, "standard_b64decode"),
    (base64, "decodebytes"),
    (binascii, "a2b_base64"),
    (email.base64mime, "a2b_base64"),
    (email.base64mime, "decode"),
    (fake_gmail, "b64url_decode"),
]


@pytest.fixture
def decoder_calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Replace every base64 decoder by a spy that records its name and then raises."""
    calls: list[str] = []

    def spy(label: str) -> Callable[..., bytes]:
        def decoder(*args: object, **kwargs: object) -> bytes:
            calls.append(label)
            raise AssertionError(f"{label} was called")

        return decoder

    for module, name in DECODERS:
        monkeypatch.setattr(module, name, spy(f"{module.__name__}.{name}"))
    return calls


def _sentinel_message() -> MessageBuilder:
    builder = MessageBuilder("m1").text(SENTINEL_SENTENCE)
    builder.attachment(
        "scan.pdf", "application/octet-stream", SENTINEL_SENTENCE.encode(), inline=True
    )
    return builder


# ------------------------------------------------------------------ AC-6
def test_a_message_with_only_a_drive_link_yields_no_pdf_part() -> None:
    message = MessageBuilder("m1").text("See the file in Drive.").html(DRIVE_LINK).build()

    parts = part_infos(message.resource["payload"])

    assert [part.mime_type for part in parts] == ["multipart/mixed", "text/plain", "text/html"]
    assert [is_pdf_part(part) for part in parts] == [False, False, False]


def test_a_drive_link_in_the_plain_text_body_yields_no_pdf_part() -> None:
    link = "https://drive.google.com/file/d/SYNTHETIC-FILE-ID/view?name=Invoice.pdf"
    message = MessageBuilder("m1").text(link).build()

    assert not any(is_pdf_part(part) for part in part_infos(message.resource["payload"]))


def test_a_drive_link_in_a_nested_html_alternative_yields_no_pdf_part() -> None:
    builder = MessageBuilder("m1")
    with builder.multipart("alternative"):
        builder.text(DRIVE_LINK)
        builder.html(DRIVE_LINK)
    message = builder.build()

    parts = part_infos(message.resource["payload"])

    assert len(parts) == 4
    assert not any(is_pdf_part(part) for part in parts)


def test_the_same_message_with_a_real_pdf_part_yields_exactly_that_part() -> None:
    message = MessageBuilder("m1").html(DRIVE_LINK).pdf("Invoice.pdf").build()

    found = [part for part in part_infos(message.resource["payload"]) if is_pdf_part(part)]

    assert [(part.mime_type, part.filename) for part in found] == [
        ("application/pdf", "Invoice.pdf")
    ]


# ------------------------------------------------------------------ AC-7
def test_the_sentinel_really_sits_in_the_message_body() -> None:
    payload = _sentinel_message().build().resource["payload"]

    bodies = [part["body"].get("data") for part in iter_parts(payload)]

    assert b64url_encode(SENTINEL_SENTENCE.encode()) in bodies
    assert b64url_decode(b64url_encode(SENTINEL_SENTENCE.encode())).decode() == SENTINEL_SENTENCE


def test_the_rule_runs_without_reading_a_body_or_decoding_anything(
    decoder_calls: list[str],
) -> None:
    payload = _sentinel_message().build().resource["payload"]
    reads: list[tuple[str, ...]] = []

    parts = part_infos(RecordingMapping(payload, reads))
    verdicts = [is_pdf_part(part) for part in parts]

    assert verdicts == [False, False, True]
    assert decoder_calls == []
    assert {read[-1] for read in reads} <= ALLOWED_READS
    assert not any("data" in read for read in reads)
    assert not any(read[-1] == "*" for read in reads)  # nothing was read by iterating


def test_the_recording_shows_that_type_and_name_were_read() -> None:
    payload = _sentinel_message().build().resource["payload"]
    reads: list[tuple[str, ...]] = []

    part_infos(RecordingMapping(payload, reads))

    assert ("mimeType",) in reads
    assert ("filename",) in reads
    assert ("body", "size") in reads
    assert ("body", "attachmentId") in reads


def test_a_mapping_that_reads_the_body_would_be_caught() -> None:
    payload = _sentinel_message().build().resource["payload"]
    reads: list[tuple[str, ...]] = []
    greedy = RecordingMapping(payload, reads)

    for part in iter_parts(greedy):
        body = part["body"]
        assert isinstance(body, Mapping)
        body.get("data")

    assert any(read[-1] == "data" for read in reads)


def test_a_mapping_that_iterates_a_part_would_be_caught() -> None:
    reads: list[tuple[str, ...]] = []

    list(RecordingMapping({"partId": "1"}, reads))

    assert reads == [("*",)]


def test_a_membership_test_on_the_body_is_recorded() -> None:
    reads: list[tuple[str, ...]] = []
    body = RecordingMapping({"body": {"data": "x"}}, reads)["body"]

    assert isinstance(body, Mapping)
    assert "data" in body
    assert ("body", "data") in reads


def test_a_decode_through_the_fake_helper_is_recorded_by_the_spy(
    decoder_calls: list[str],
) -> None:
    with pytest.raises(AssertionError, match="b64url_decode"):
        fake_gmail.b64url_decode("AAAA")

    assert decoder_calls == ["tests.fakes.fake_gmail.b64url_decode"]


@pytest.mark.parametrize(("module", "name"), DECODERS[:-1])
def test_every_standard_decoder_spy_is_recorded(
    decoder_calls: list[str], module: object, name: str
) -> None:
    with pytest.raises(AssertionError, match=name):
        getattr(module, name)("AAAA")

    assert len(decoder_calls) == 1


def test_a_part_with_an_encoded_name_still_decodes_no_base64_body(
    decoder_calls: list[str],
) -> None:
    # A name that is an encoded word is decoded by design (AC-5); that is the name, not the body.
    # Only a Q word is used: a B word (base64) goes through the stdlib decoder, which is allowed
    # for names and is covered by the AC-5 rows of test_mime_pdf_rule.py.
    part = PartInfo("1", "application/octet-stream", "=?utf-8?q?a.pdf?=", 0, False)

    assert is_pdf_part(part) is True
    assert decoder_calls == []


# ------------------------------------------------------------------ PartInfo shape
def test_part_info_has_five_metadata_fields_and_none_for_content() -> None:
    names = [field.name for field in fields(PartInfo)]

    assert names == ["part_id", "mime_type", "filename", "size", "has_attachment_id"]
    assert not {"data", "body", "content", "bytes", "text", "payload"} & set(names)


def test_part_info_built_from_a_sentinel_part_holds_no_trace_of_the_body() -> None:
    payload = _sentinel_message().build().resource["payload"]
    infos = part_infos(payload)

    text = repr(infos)
    assert SENTINEL_SENTENCE not in text
    assert b64url_encode(SENTINEL_SENTENCE.encode()) not in text
    assert not any(hasattr(info, "data") for info in infos)


def test_part_info_is_frozen_slotted_and_hashable() -> None:
    info = PartInfo("1.2", "application/pdf", "a.pdf", 10, True)

    attribute = "filename"
    with pytest.raises(FrozenInstanceError):
        setattr(info, attribute, "b.pdf")
    assert not hasattr(info, "__dict__")
    assert hash(info) == hash(PartInfo("1.2", "application/pdf", "a.pdf", 10, True))


def test_the_mapping_reads_size_and_attachment_id_from_the_body() -> None:
    message = MessageBuilder("m1").pdf("a.pdf", content=b"%PDF-1.4\n" + b"x" * 20).build()
    root, pdf = part_infos(message.resource["payload"])

    assert (pdf.part_id, pdf.mime_type, pdf.filename) == ("0", "application/pdf", "a.pdf")
    assert pdf.size == 29
    assert pdf.has_attachment_id is True
    assert (root.part_id, root.size, root.has_attachment_id) == ("", 0, False)


def test_the_mapping_of_an_inline_part_has_no_attachment_id() -> None:
    message = MessageBuilder("m1").pdf("a.pdf", content=b"x" * 5, inline=True).build()

    info = part_infos(message.resource["payload"])[1]

    assert (info.size, info.has_attachment_id) == (5, False)


@pytest.mark.parametrize(
    "resource",
    [{}, {"body": None}, {"body": "x"}, {"body": {"size": "7"}}, {"partId": 3, "mimeType": None}],
)
def test_the_mapping_tolerates_missing_or_odd_fields(resource: dict[str, object]) -> None:
    info = part_info(resource)

    assert isinstance(info, PartInfo)
    assert (info.size, info.has_attachment_id) == (0, False)


def test_part_infos_walk_in_document_order() -> None:
    builder = MessageBuilder("m1").text()
    with builder.multipart("related"):
        builder.pdf("a.pdf")
    builder.pdf("b.pdf")

    ids = [info.part_id for info in part_infos(builder.build().resource["payload"])]

    assert ids == ["", "0", "1", "1.0", "2"]
