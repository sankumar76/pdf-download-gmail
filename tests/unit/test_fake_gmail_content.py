"""AC-7: FakeGmail message resources and attachment bodies."""

from __future__ import annotations

import pytest

from tests.fakes.fake_gmail import FakeGmail, FakeGmailHttpError, b64url_decode, iter_parts
from tests.fixtures.builders import MessageBuilder

pytestmark = pytest.mark.req("NFR-022", "AC-7")


def _nested_message() -> FakeGmail:
    inner = MessageBuilder().subject("inner").pdf("inner.pdf")
    message = MessageBuilder("m1").text()
    with message.multipart("related"), message.multipart("alternative"):
        message.pdf("deep.pdf")
    message.forwarded(inner)
    return FakeGmail([message.build()])


def _named_parts(fake: FakeGmail) -> dict[str, dict[str, object]]:
    payload = fake.get_message("m1")["payload"]
    return {p["filename"]: p for p in iter_parts(payload) if p["filename"]}


def test_get_message_returns_an_independent_copy() -> None:
    fake = FakeGmail([MessageBuilder("m1").pdf("a.pdf").build()])
    first = fake.get_message("m1")

    first["payload"]["parts"].clear()

    assert fake.get_message("m1")["payload"]["parts"]


def test_get_message_unknown_id_is_http_404() -> None:
    with pytest.raises(FakeGmailHttpError) as exc_info:
        FakeGmail().get_message("missing")

    assert exc_info.value.status == 404


def test_part_inside_nested_multipart_has_a_dotted_part_id() -> None:
    assert _named_parts(_nested_message())["deep.pdf"]["partId"] == "1.0.0"


def test_forwarded_message_part_nests_the_inner_message_parts() -> None:
    fake = _nested_message()

    assert _named_parts(fake)["inner.pdf"]["partId"].count(".") >= 2
    assert "message/rfc822" in {
        p["mimeType"] for p in iter_parts(fake.get_message("m1")["payload"])
    }


def test_nested_multipart_mime_types_are_present() -> None:
    payload = _nested_message().get_message("m1")["payload"]

    assert {"multipart/related", "multipart/alternative"} <= {
        p["mimeType"] for p in iter_parts(payload)
    }


def test_attachment_id_body_is_served_by_get_attachment() -> None:
    content = b"%PDF-1.4 distinctive"
    fake = FakeGmail([MessageBuilder("m1").pdf("big.pdf", content=content).build()])
    body = _named_parts(fake)["big.pdf"]["body"]

    assert "data" not in body
    assert fake.get_attachment("m1", body["attachmentId"]) == content


def test_inline_body_carries_its_bytes_in_body_data() -> None:
    message = MessageBuilder("m1").pdf("small.pdf", content=b"abc", inline=True).build()
    body = _named_parts(FakeGmail([message]))["small.pdf"]["body"]

    assert "attachmentId" not in body
    assert b64url_decode(body["data"]) == b"abc"


@pytest.mark.parametrize(
    ("message_id", "attachment_id"),
    [
        pytest.param("m1", "nope", id="unknown-attachment-id"),
        pytest.param("missing", "att-m1-1", id="unknown-message"),
    ],
)
def test_get_attachment_unknown_ids_are_http_404(message_id: str, attachment_id: str) -> None:
    fake = FakeGmail([MessageBuilder("m1").pdf("a.pdf").build()])

    with pytest.raises(FakeGmailHttpError) as exc_info:
        fake.get_attachment(message_id, attachment_id)

    assert exc_info.value.status == 404
