"""GitHub #13 (QUA-06): MessageBuilder gives file parts the headers real Gmail parts carry.

``format=full`` parts have ``Content-Type`` (with ``name=``), ``Content-Disposition`` (with
``filename=``) and ``Content-Transfer-Encoding``. The builder emits these by default and accepts
``headers=`` to add to them or replace them. Container and text parts stay header-less.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from email import message_from_string
from email.message import Message
from email.utils import collapse_rfc2231_value

import pytest

from tests.fakes.fake_gmail import b64url_decode, iter_parts
from tests.fixtures.builders import MessageBuilder

pytestmark = pytest.mark.req("QUA-06", "RISK-021")

Header = tuple[str, str]


def _file_part_headers(builder: MessageBuilder) -> list[Header]:
    part = builder.build("m1").resource["payload"]["parts"][0]
    return [(h["name"], h["value"]) for h in part["headers"]]


def _first(headers: Sequence[Header], name: str) -> str:
    return next(value for key, value in headers if key == name)


def _parsed(headers: Sequence[Header]) -> Message:
    """The headers read back by the standard library, as a consumer of real mail would."""
    text = "".join(f"{name}: {value}\n" for name, value in headers) + "\n"
    return message_from_string(text)


def test_default_content_type_carries_the_mime_type_and_the_name() -> None:
    headers = _file_part_headers(MessageBuilder().pdf("Invoice.pdf"))

    assert _first(headers, "Content-Type") == 'application/pdf; name="Invoice.pdf"'


def test_default_content_disposition_is_attachment_with_the_filename() -> None:
    headers = _file_part_headers(MessageBuilder().pdf("Invoice.pdf"))

    assert _first(headers, "Content-Disposition") == 'attachment; filename="Invoice.pdf"'


def test_default_transfer_encoding_is_base64() -> None:
    headers = _file_part_headers(MessageBuilder().pdf("Invoice.pdf"))

    assert _first(headers, "Content-Transfer-Encoding") == "base64"


def test_the_three_defaults_are_the_only_headers_and_come_in_that_order() -> None:
    headers = _file_part_headers(MessageBuilder().pdf("Invoice.pdf"))

    assert [name for name, _ in headers] == [
        "Content-Type",
        "Content-Disposition",
        "Content-Transfer-Encoding",
    ]


def test_an_attachment_of_another_type_uses_its_own_mime_type() -> None:
    builder = MessageBuilder().attachment("data.bin", "application/octet-stream", b"x")

    assert _first(_file_part_headers(builder), "Content-Type") == (
        'application/octet-stream; name="data.bin"'
    )


def test_an_inline_part_gets_an_inline_disposition() -> None:
    headers = _file_part_headers(MessageBuilder().pdf("Scan.pdf", inline=True))

    assert _first(headers, "Content-Disposition") == 'inline; filename="Scan.pdf"'


def test_a_part_without_a_name_has_no_name_parameter() -> None:
    headers = _file_part_headers(MessageBuilder().pdf(None))

    assert _first(headers, "Content-Type") == "application/pdf"
    assert _first(headers, "Content-Disposition") == "attachment"
    assert _first(headers, "Content-Transfer-Encoding") == "base64"


def test_an_empty_name_is_the_same_as_no_name() -> None:
    headers = _file_part_headers(MessageBuilder().pdf(""))

    assert _first(headers, "Content-Type") == "application/pdf"


@pytest.mark.parametrize(
    "name",
    ["Invoice.pdf", 'say "hi".pdf', "back\\slash.pdf", "résumé.pdf", "テスト.pdf", "a b; c=d.pdf"],
)
def test_default_headers_read_back_as_the_name_given(name: str) -> None:
    parsed = _parsed(_file_part_headers(MessageBuilder().pdf(name)))

    assert parsed.get_filename() == name
    assert collapse_rfc2231_value(parsed.get_param("name") or "") == name


def test_a_non_ascii_name_is_written_in_the_rfc_2231_form() -> None:
    headers = _file_part_headers(MessageBuilder().pdf("résumé.pdf"))

    assert _first(headers, "Content-Disposition").startswith("attachment; filename*=")
    assert _first(headers, "Content-Type").isascii()


def test_the_gmail_filename_field_is_unchanged_by_the_headers() -> None:
    part = MessageBuilder().pdf("Invoice.pdf").build("m1").resource["payload"]["parts"][0]

    assert part["filename"] == "Invoice.pdf"
    assert part["mimeType"] == "application/pdf"


def test_extra_headers_follow_the_defaults_in_the_order_given() -> None:
    headers = _file_part_headers(
        MessageBuilder().pdf("a.pdf", headers=[("Content-ID", "<c1>"), ("X-Note", "n")])
    )

    assert headers[-2:] == [("Content-ID", "<c1>"), ("X-Note", "n")]
    assert len(headers) == 5


def test_an_override_replaces_the_default_of_the_same_name() -> None:
    headers = _file_part_headers(
        MessageBuilder().pdf("a.pdf", headers=[("Content-Disposition", "inline")])
    )

    assert [v for k, v in headers if k == "Content-Disposition"] == ["inline"]
    assert _first(headers, "Content-Type") == 'application/pdf; name="a.pdf"'


def test_an_override_matches_the_header_name_without_regard_to_case() -> None:
    headers = _file_part_headers(
        MessageBuilder().attachment(
            "a.pdf", "application/octet-stream", b"x", headers=[("content-type", "text/x-odd")]
        )
    )

    assert [(k, v) for k, v in headers if k.lower() == "content-type"] == [
        ("content-type", "text/x-odd")
    ]


def test_a_repeated_override_name_keeps_every_given_value() -> None:
    headers = _file_part_headers(
        MessageBuilder().pdf("a.pdf", headers=[("Received", "one"), ("Received", "two")])
    )

    assert [v for k, v in headers if k == "Received"] == ["one", "two"]


def test_an_override_can_hold_an_rfc_2047_name_the_default_cannot() -> None:
    encoded = 'application/octet-stream; name="=?utf-8?q?a.pdf?="'
    headers = _file_part_headers(
        MessageBuilder().attachment(
            "", "application/octet-stream", b"x", headers=[("Content-Type", encoded)]
        )
    )

    assert _first(headers, "Content-Type") == encoded


def test_the_caller_list_is_not_modified() -> None:
    extra: list[Header] = [("Content-Type", "x/y")]

    MessageBuilder().pdf("a.pdf", headers=extra).build("m1")

    assert extra == [("Content-Type", "x/y")]


def test_every_part_added_gets_its_own_headers() -> None:
    builder = MessageBuilder().pdf("a.pdf").pdf("b.pdf", headers=[("X-Note", "n")])

    parts = builder.build("m1").resource["payload"]["parts"]

    assert _first([(h["name"], h["value"]) for h in parts[0]["headers"]], "Content-Type") == (
        'application/pdf; name="a.pdf"'
    )
    assert [h["name"] for h in parts[1]["headers"]][-1] == "X-Note"
    assert all(h["name"] != "X-Note" for h in parts[0]["headers"])


def test_a_part_inside_a_multipart_gets_defaults_too() -> None:
    builder = MessageBuilder()
    with builder.multipart("related"):
        builder.pdf("deep.pdf")

    parts = [p for p in iter_parts(builder.build("m1").resource["payload"]) if p["filename"]]

    assert [h["name"] for h in parts[0]["headers"]][0] == "Content-Type"


def test_containers_and_text_parts_stay_header_less() -> None:
    builder = MessageBuilder().text("hello")
    with builder.multipart("related"):
        builder.pdf("deep.pdf")

    parts = list(iter_parts(builder.build("m1").resource["payload"]))
    by_type: Mapping[str, list[object]] = {p["mimeType"]: p["headers"] for p in parts[1:]}

    assert by_type["text/plain"] == []
    assert by_type["multipart/related"] == []


def test_the_root_keeps_its_envelope_headers() -> None:
    root = MessageBuilder().subject("Hello").pdf("a.pdf").build("m1").resource["payload"]

    assert {h["name"] for h in root["headers"]} == {"From", "To", "Subject", "Date"}


def test_a_forwarded_message_part_is_header_less_and_its_inner_pdf_has_defaults() -> None:
    message = MessageBuilder().forwarded(MessageBuilder().pdf("Inner.pdf")).build("m1")
    parts = list(iter_parts(message.resource["payload"]))
    wrapper = next(p for p in parts if p["mimeType"] == "message/rfc822")
    inner = next(p for p in parts if p["filename"] == "Inner.pdf")

    assert wrapper["headers"] == []
    assert _first([(h["name"], h["value"]) for h in inner["headers"]], "Content-Type") == (
        'application/pdf; name="Inner.pdf"'
    )


def test_an_html_part_is_an_inline_text_html_body_without_headers() -> None:
    root = MessageBuilder().html("<p>Hello</p>").build("m1").resource["payload"]
    part = root["parts"][0]

    assert part["mimeType"] == "text/html"
    assert part["filename"] == ""
    assert part["headers"] == []
    assert b64url_decode(part["body"]["data"]) == b"<p>Hello</p>"
