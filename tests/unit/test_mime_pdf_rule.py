"""STORY-03.01 AC-1..AC-5 and AC-8: which part metadata is a PDF (FR-019, BR-008, EC-04).

Table-driven: one row per (type, filename) pair. Every decoding row also proves the function
returns a bool or a str and never raises, whatever the name holds (AC-5, undecodable names).
All names are synthetic.
"""

from __future__ import annotations

import base64

import pytest

from gmail_pdf.domain import mime
from gmail_pdf.domain.mime import decode_part_name, is_pdf_part, normalise_content_type
from gmail_pdf.domain.models import PartInfo

pytestmark = pytest.mark.req("FR-019", "BR-008")

PDF = "application/pdf"
OCTET = "application/octet-stream"
REPLACEMENT = "�"


def part(mime_type: str, filename: str = "") -> PartInfo:
    """A part with the given type and Gmail ``filename``; the other fields do not matter."""
    return PartInfo(
        part_id="1", mime_type=mime_type, filename=filename, size=0, has_attachment_id=False
    )


def b64_word(text: str, charset: str = "utf-8") -> str:
    """An RFC 2047 ``B`` encoded word for ``text``."""
    payload = base64.b64encode(text.encode(charset)).decode("ascii")
    return f"=?{charset}?B?{payload}?="


# ------------------------------------------------------------------ AC-1 .. AC-4, AC-8
RULE_ROWS = [
    # AC-1: application/pdf is a PDF whatever the name is, an empty one included.
    pytest.param(PDF, "a.pdf", True, id="AC-1 pdf type with a pdf name"),
    pytest.param(PDF, "", True, id="AC-1 pdf type with an empty name"),
    pytest.param(PDF, "notes.txt", True, id="AC-1 pdf type with another extension"),
    pytest.param(PDF, "no-extension", True, id="AC-1 pdf type with no extension"),
    pytest.param(PDF, "=?nosuch?q?a?=", True, id="AC-1 pdf type with an undecodable name"),
    # AC-2: octet-stream is a PDF when the name ends in .pdf, in any case.
    pytest.param(OCTET, "a.pdf", True, id="AC-2 .pdf"),
    pytest.param(OCTET, "a.PDF", True, id="AC-2 .PDF"),
    pytest.param(OCTET, "a.Pdf", True, id="AC-2 .Pdf"),
    pytest.param(OCTET, "a.pDF", True, id="AC-2 .pDF"),
    pytest.param(OCTET, "multi.dot.name.pdf", True, id="AC-2 several dots"),
    pytest.param(OCTET, "x.pdf.pdf", True, id="AC-2 pdf twice"),
    pytest.param(OCTET, "résumé.pdf", True, id="AC-2 accented name"),
    pytest.param(OCTET, "日本語.PDF", True, id="AC-2 non-latin name"),
    pytest.param(OCTET, "a b (1).pdf", True, id="AC-2 spaces and brackets"),
    pytest.param(OCTET, ".pdf", True, id="AC-2 only the extension (the rule is the suffix)"),
    # AC-3: octet-stream with any other name is not a PDF.
    pytest.param(OCTET, "data.bin", False, id="AC-3 data.bin"),
    pytest.param(OCTET, "x.pdf.exe", False, id="AC-3 x.pdf.exe"),
    pytest.param(OCTET, "pdf", False, id="AC-3 pdf without a dot"),
    pytest.param(OCTET, "", False, id="AC-3 empty name"),
    pytest.param(OCTET, "apdf", False, id="AC-3 ends in pdf without the dot"),
    pytest.param(OCTET, "a_pdf", False, id="AC-3 underscore before pdf"),
    pytest.param(OCTET, "a.pdfx", False, id="AC-3 longer extension"),
    pytest.param(OCTET, "a.pd", False, id="AC-3 shorter extension"),
    pytest.param(OCTET, "a.pdf/", False, id="AC-3 slash after the extension"),
    # AC-4: any other type is not a PDF, whatever the name says.
    pytest.param("text/plain", "x.pdf", False, id="AC-4 text/plain"),
    pytest.param("text/html", "x.pdf", False, id="AC-4 text/html"),
    pytest.param("image/png", "x.pdf", False, id="AC-4 image/png"),
    pytest.param("application/zip", "x.pdf", False, id="AC-4 application/zip"),
    pytest.param("message/rfc822", "x.pdf", False, id="AC-4 message/rfc822"),
    pytest.param("multipart/mixed", "x.pdf", False, id="AC-4 multipart/mixed"),
    pytest.param("", "x.pdf", False, id="AC-4 empty type"),
    pytest.param("application/pdfx", "x.pdf", False, id="AC-4 type that only starts like pdf"),
    pytest.param("xapplication/pdf", "x.pdf", False, id="AC-4 type that only ends like pdf"),
    # AC-8: surrounding whitespace is stripped, a trailing dot is not.
    pytest.param(OCTET, "a.pdf ", True, id="AC-8 trailing space"),
    pytest.param(OCTET, " a.PDF", True, id="AC-8 leading space"),
    pytest.param(OCTET, "\ta.pdf\r\n", True, id="AC-8 tab and line end"),
    pytest.param(OCTET, " a.pdf ", True, id="AC-8 no-break spaces"),
    pytest.param(OCTET, "a.pdf.", False, id="AC-8 trailing dot"),
    pytest.param(OCTET, "a.pdf. ", False, id="AC-8 trailing dot then space"),
    pytest.param(OCTET, "a.pdf .", False, id="AC-8 space inside before a dot"),
    pytest.param(OCTET, "   ", False, id="AC-8 only whitespace"),
    pytest.param(OCTET, "a. pdf", False, id="AC-8 space inside the extension"),
]


@pytest.mark.parametrize(("mime_type", "filename", "expected"), RULE_ROWS)
def test_type_and_name_matrix(mime_type: str, filename: str, expected: bool) -> None:
    assert is_pdf_part(part(mime_type, filename)) is expected


def test_the_name_is_not_decoded_when_the_type_already_says_pdf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(name: str) -> str:
        raise AssertionError("an application/pdf part needs no name")

    monkeypatch.setattr(mime, "decode_part_name", forbidden)

    assert is_pdf_part(part(PDF, "=?utf-8?q?a?=")) is True


def test_other_fields_of_the_part_do_not_change_the_answer() -> None:
    plain = PartInfo("0.1", PDF, "", 0, False)
    other = PartInfo("9.9.9", PDF, "", 123456, True)

    assert is_pdf_part(plain) is is_pdf_part(other) is True


# ------------------------------------------------------------------ AC-5: content type
TYPE_ROWS = [
    ("application/pdf", "application/pdf"),
    ("Application/PDF", "application/pdf"),
    ('Application/PDF; name="a.pdf"', "application/pdf"),
    ("application/pdf;name=a.pdf", "application/pdf"),
    ("  application/pdf  ;  x=y", "application/pdf"),
    ("\tAPPLICATION/OCTET-STREAM\r\n", "application/octet-stream"),
    ('text/plain; charset="utf-8"', "text/plain"),
    ('application/pdf; name="a;b.pdf"', "application/pdf"),
    ("", ""),
    (";charset=utf-8", ""),
    ("   ", ""),
]


@pytest.mark.parametrize(("raw", "expected"), TYPE_ROWS)
def test_content_type_is_lower_case_without_parameters(raw: str, expected: str) -> None:
    assert normalise_content_type(raw) == expected


@pytest.mark.parametrize(
    ("raw", "filename", "expected"),
    [
        pytest.param('Application/PDF; name="a.pdf"', "", True, id="AC-5 pdf with parameters"),
        pytest.param("APPLICATION/PDF", "x.txt", True, id="AC-5 upper case pdf"),
        pytest.param(" application/pdf ", "", True, id="AC-5 padded pdf"),
        pytest.param("Application/Octet-Stream; name=a.pdf", "a.pdf", True, id="AC-5 octet pdf"),
        pytest.param("Application/Octet-Stream; name=a.pdf", "a.bin", False, id="AC-5 octet bin"),
        pytest.param('Text/Plain; name="a.pdf"', "a.pdf", False, id="AC-5 text with a pdf name"),
    ],
)
def test_a_type_with_case_or_parameters_is_read_as_its_type(
    raw: str, filename: str, expected: bool
) -> None:
    assert is_pdf_part(part(raw, filename)) is expected


# ------------------------------------------------------------------ AC-5: encoded names
DECODE_ROWS = [
    # plain names are returned as they are
    ("plain.pdf", "plain.pdf"),
    ("", ""),
    ("O'Brien.pdf", "O'Brien.pdf"),
    ("it's a 'x.pdf", "it's a 'x.pdf"),
    ("utf-8*en''x.pdf", "utf-8*en''x.pdf"),
    # RFC 2047, Q and B, any charset case
    ("=?utf-8?q?r=C3=A9sum=C3=A9.pdf?=", "résumé.pdf"),
    ("=?UTF-8?Q?r=C3=A9sum=C3=A9.pdf?=", "résumé.pdf"),
    (b64_word("résumé.pdf"), "résumé.pdf"),
    (b64_word("日本語.PDF"), "日本語.PDF"),
    ("=?iso-8859-1?q?r=E9sum=E9.pdf?=", "résumé.pdf"),
    (b64_word("résumé.pdf", "iso-8859-1"), "résumé.pdf"),
    ("=?utf-8?q?a_b.pdf?=", "a b.pdf"),
    ("=?utf-8*en?q?a.pdf?=", "a.pdf"),
    ("=?utf-8?q??=", ""),
    # words, text between them, and the whitespace between two words (RFC 2047 section 6.2)
    ("=?utf-8?q?a?= =?utf-8?q?.pdf?=", "a.pdf"),
    ("=?utf-8?q?a?=   =?utf-8?q?.pdf?=", "a.pdf"),
    ("=?utf-8?q?a?=\t=?utf-8?q?b?=", "ab"),
    ("=?utf-8?q?a?==?utf-8?q?b?=", "ab"),
    ("=?utf-8?q?a?=x=?utf-8?q?.pdf?=", "ax.pdf"),
    ("x =?utf-8?q?a?= y", "x a y"),
    ("report_=?utf-8?q?=C3=A9?=.pdf", "report_é.pdf"),
    ("=?utf-8?q?a.pdf=20?=", "a.pdf "),
    # RFC 2231 values: charset'language'percent-encoded
    ("utf-8''r%C3%A9sum%C3%A9.pdf", "résumé.pdf"),
    ("UTF-8'de'r%C3%A9sum%C3%A9.pdf", "résumé.pdf"),
    ("iso-8859-1'en'r%E9sum%E9.pdf", "résumé.pdf"),
    ("utf-8''a%20b.pdf", "a b.pdf"),
    ("utf-8''a%2Epdf", "a.pdf"),
    ("utf-8''plain.pdf", "plain.pdf"),
    ("utf-8''", ""),
    ("utf-8''é.pdf", "é.pdf"),
    # undecodable names (no new AC): bad bytes become U+FFFD, bad fragments stay as received
    ("=?utf-8?q?=FF=FE.pdf?=", REPLACEMENT * 2 + ".pdf"),
    ("=?utf-8?b?/w==?=.pdf", REPLACEMENT + ".pdf"),
    ("utf-8''%FF.pdf", REPLACEMENT + ".pdf"),
    ("ascii''%FF%FF", REPLACEMENT * 2),
    ("=?nosuch?q?a.pdf?=", "=?nosuch?q?a.pdf?="),
    ("=?nosuch?q??=", "=?nosuch?q??="),
    ("=?utf-8?b?A?=", "=?utf-8?b?A?="),
    ("=?utf-8?b?A?=.pdf", "=?utf-8?b?A?=.pdf"),
    ("=?utf-8?x?a.pdf?=", "=?utf-8?x?a.pdf?="),
    ("=?utf-8?q?a.pdf", "=?utf-8?q?a.pdf"),
    ("=?", "=?"),
    ("=?utf-8?q?a?= =?nosuch?q?b?=", "a=?nosuch?q?b?="),
    ("=?nosuch?q?a?= =?utf-8?q?b?=", "=?nosuch?q?a?=b"),
    ("=?rot13?q?a?=", "=?rot13?q?a?="),
    ("nosuch''a.pdf", "nosuch''a.pdf"),
    ("nosuch''a%2Epdf", "nosuch''a%2Epdf"),
    ("rot13''a%2Epdf", "rot13''a%2Epdf"),
    ("idna''abc", "idna''abc"),
    ("a\x00b''abc", "a\x00b''abc"),
    ("utf-8''\ud800.pdf", "utf-8''\ud800.pdf"),
    ("\ud800.pdf", "\ud800.pdf"),
    ("=?utf-8?b?\ud800?=.pdf", "=?utf-8?b?\ud800?=.pdf"),
]


@pytest.mark.parametrize(("raw", "expected"), DECODE_ROWS, ids=[repr(r[0]) for r in DECODE_ROWS])
def test_decode_part_name_never_raises_and_gives_the_documented_text(
    raw: str, expected: str
) -> None:
    assert decode_part_name(raw) == expected


def test_a_very_long_name_is_handled() -> None:
    long_name = "a" * 100_000 + ".pdf"

    assert decode_part_name(long_name) == long_name
    assert is_pdf_part(part(OCTET, long_name)) is True


def test_many_unfinished_words_are_returned_as_received() -> None:
    name = "=?a?q?" * 5_000

    assert decode_part_name(name) == name


ENCODED_NAME_ROWS = [
    pytest.param(b64_word("résumé.pdf"), True, id="AC-5 base64 word"),
    pytest.param("=?utf-8?q?r=C3=A9sum=C3=A9.PDF?=", True, id="AC-5 quoted-printable word"),
    pytest.param("=?iso-8859-1?q?r=E9sum=E9.pdf?=", True, id="AC-5 latin-1 word"),
    pytest.param("=?utf-8?q?a?= =?utf-8?q?.pdf?=", True, id="AC-5 name split in two words"),
    pytest.param("report_=?utf-8?q?=C3=A9?=.pdf", True, id="AC-5 word inside a name"),
    pytest.param("utf-8''r%C3%A9sum%C3%A9.pdf", True, id="AC-5 rfc 2231 utf-8"),
    pytest.param("iso-8859-1'en'r%E9sum%E9.PDF", True, id="AC-5 rfc 2231 latin-1 with language"),
    pytest.param("utf-8''a%2Epdf", True, id="AC-5 rfc 2231 encoded dot"),
    pytest.param("=?utf-8?q?a.pdf=20?=", True, id="AC-8 word that decodes to a trailing space"),
    pytest.param("=?utf-8?q?=20a.pdf?=", True, id="AC-8 word that decodes to a leading space"),
    pytest.param("=?utf-8?q?a.exe?=", False, id="AC-5 word that decodes to another extension"),
    pytest.param("=?utf-8?q?a.pdf?=.exe", False, id="AC-5 word then another extension"),
    pytest.param("=?utf-8?q?a.pdf.?=", False, id="AC-8 word that decodes to a trailing dot"),
    pytest.param("utf-8''a.pdf%2Eexe", False, id="AC-5 rfc 2231 other extension"),
    # undecodable names: no exception, the ordinary test on what is left
    pytest.param("=?nosuch?q?a.pdf?=", False, id="undecodable unknown charset stays as received"),
    pytest.param("=?nosuch?q?a?=.pdf", True, id="undecodable word then .pdf"),
    pytest.param("=?utf-8?q?=FF=FE.pdf?=", True, id="undecodable bytes keep the extension"),
    pytest.param("=?utf-8?b?/w==?=.pdf", True, id="undecodable base64 bytes keep the extension"),
    pytest.param("utf-8''%FF.pdf", True, id="undecodable rfc 2231 bytes keep the extension"),
    pytest.param("=?utf-8?b?A?=", False, id="undecodable bad base64 stays as received"),
    pytest.param("=?utf-8?b?A?=.pdf", True, id="undecodable bad base64 then .pdf"),
    pytest.param("=?utf-8?q?a.pdf", True, id="unfinished word ends in .pdf as received"),
    pytest.param("=?utf-8?q?a.pdf?", False, id="undecodable unfinished word"),
    pytest.param("=?", False, id="undecodable lone opener"),
    pytest.param("nosuch''a%2Epdf", False, id="undecodable rfc 2231 unknown charset"),
    pytest.param("nosuch''a.pdf", True, id="rfc 2231 unknown charset, plain .pdf at the end"),
    pytest.param("idna''abc.pdf", True, id="undecodable codec error stays as received"),
    pytest.param("a\x00b''abc", False, id="undecodable charset with a NUL"),
    pytest.param("\ud800.pdf", True, id="lone surrogate"),
    pytest.param("utf-8''\ud800", False, id="lone surrogate in an rfc 2231 value"),
]


@pytest.mark.parametrize(("filename", "expected"), ENCODED_NAME_ROWS)
def test_an_octet_stream_part_is_judged_on_the_decoded_name(filename: str, expected: bool) -> None:
    assert is_pdf_part(part(OCTET, filename)) is expected


@pytest.mark.parametrize(
    "filename",
    [row[0] for row in DECODE_ROWS]
    + ["=?utf-8?q?" * 50, "'" * 10, "''", "'a'", "\x00", "=?\x00?q?\x00?=", "%" * 20, "%zz"],
)
def test_no_name_makes_the_rule_raise(filename: str) -> None:
    assert isinstance(is_pdf_part(part(OCTET, filename)), bool)
    assert isinstance(is_pdf_part(part(PDF, filename)), bool)
