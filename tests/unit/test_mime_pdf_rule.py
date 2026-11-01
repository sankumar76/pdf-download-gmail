"""STORY-03.01 AC-1..AC-5 and AC-8: which part metadata is a PDF (FR-019, BR-008, EC-04).

Table-driven: one row per (type, filename) pair. Every decoding row also proves the function
returns a bool or a str and never raises, whatever the name holds (AC-5, undecodable names).
All names are synthetic.
"""

from __future__ import annotations

import base64
import codecs
import encodings
import time
from dataclasses import dataclass, field
from typing import Any

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
    # a charset is matched lower-cased, with ``_`` read as ``-`` and a ``*language`` tag removed
    ("=?UTF_8?q?a.pdf?=", "a.pdf"),
    ("=?Utf-8*EN?q?a.pdf?=", "a.pdf"),
    ("=?ISO_8859_1?q?r=E9sum=E9.pdf?=", "résumé.pdf"),
    ("=?Windows_1252?q?r=E9.pdf?=", "ré.pdf"),
    ("UTF_8''a%2Epdf", "a.pdf"),
    ("ISO_8859_1'en'r%E9sum%E9.pdf", "résumé.pdf"),
    ("LATIN1''r%E9.pdf", "ré.pdf"),
    # RFC 2231 text that is not %XX is literal: urllib's unquote decodes only the escapes (QUA-79)
    ("utf-16''a.pdf", "a.pdf"),
    ("iso-8859-1''é.pdf", "é.pdf"),
    ("ascii''é.pdf", "é.pdf"),
    # a name of the shape charset'language'text with a listed charset is read as RFC 2231, even
    # if it was an ordinary name (QUA-77, F8: the code stays and the docstring says so)
    ("latin1'draft'report.pdf", "report.pdf"),
    ("UTF8'it's'x.pdf", "s'x.pdf"),
    # white space around an RFC 2231 value is not part of it (QUA-75, F2)
    (" utf-8''a%2Epdf", "a.pdf"),
    ("utf-8''a%2Epdf ", "a.pdf"),
    ("\tutf-8''a%2Epdf\r\n", "a.pdf"),
    (" \tUTF-8'en'r%C3%A9sum%C3%A9.pdf  ", "résumé.pdf"),
    # an RFC 2047 word may hold apostrophes: a name that fails the RFC 2231 reading is then read
    # as encoded words (QUA-74, F1)
    ("=?utf-8?q?O'Brien's.pdf?=", "O'Brien's.pdf"),
    ("=?UTF-8?Q?John's_wife's_r=C3=A9sum=C3=A9.pdf?=", "John's wife's résumé.pdf"),
    ("=?iso-8859-1?q?l'=E9t=E9_d'hiver.pdf?=", "l'été d'hiver.pdf"),
    ("=?utf-8?q?a'b'c.PDF?=", "a'b'c.PDF"),
    ("=?utf-8?q?it's?==?utf-8?q?bob's.pdf?=", "it'sbob's.pdf"),
    ("report'draft' =?utf-8?q?a.pdf?=", "report'draft' a.pdf"),
    ("nosuch''=?utf-8?q?a.pdf?=", "nosuch''a.pdf"),
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
    # a lone surrogate is literal text, not a %XX run, so it passes through the charset (F7)
    ("utf-8''\ud800.pdf", "\ud800.pdf"),
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
    # QUA-74 (F1): a well-formed word with apostrophes is decoded, whatever its charset case
    pytest.param("=?utf-8?q?O'Brien's.pdf?=", True, id="AC-5 word with two apostrophes"),
    pytest.param(
        "=?UTF-8?Q?John's_wife's_r=C3=A9sum=C3=A9.pdf?=", True, id="AC-5 word, upper case"
    ),
    pytest.param(
        "=?iso-8859-1?q?l'=E9t=E9_d'hiver.pdf?=", True, id="AC-5 latin-1 word, apostrophes"
    ),
    pytest.param("=?utf-8?q?a'b'c.PDF?=", True, id="AC-5 word with apostrophes, .PDF"),
    pytest.param("=?utf-8?q?it's?==?utf-8?q?bob's.pdf?=", True, id="AC-5 two words, apostrophes"),
    pytest.param("report'draft' =?utf-8?q?a.pdf?=", True, id="AC-5 apostrophes then a word"),
    pytest.param("nosuch''=?utf-8?q?a.pdf?=", True, id="AC-5 unknown 2231 charset then a word"),
    # QUA-75 (F2): white space around an RFC 2231 value does not change the verdict
    pytest.param(" utf-8''a%2Epdf", True, id="AC-8 leading space on an rfc 2231 value"),
    pytest.param("utf-8''a%2Epdf ", True, id="AC-8 trailing space on an rfc 2231 value"),
    pytest.param("\tutf-8''a%2Epdf\r\n", True, id="AC-8 tab and line end on an rfc 2231 value"),
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
    pytest.param("utf-8''\ud800.pdf", True, id="lone surrogate in an rfc 2231 value, .pdf"),
    # QUA-79 (F7): literal text in an rfc 2231 value keeps its extension
    pytest.param("utf-16''a.pdf", True, id="rfc 2231 utf-16 with literal text"),
    pytest.param("iso-8859-1''é.pdf", True, id="rfc 2231 latin-1 with literal text"),
    pytest.param("ascii''é.pdf", True, id="rfc 2231 ascii with literal text"),
    # QUA-77 (F8): a listed charset first makes an ordinary name an rfc 2231 value; verdict holds
    pytest.param("latin1'draft'report.pdf", True, id="ordinary name read as rfc 2231, listed"),
    # QUA-76 (F6, c.10380): the verdict is pinned, not the text. A word in a listed charset is
    # decoded, whatever its text holds, so it keeps its .pdf ending.
    pytest.param("=?utf-8?q?日本.pdf?=", True, id="c.10380 raw non-ASCII text in a Q word"),
    pytest.param("=?utf-8?b?éééé?=.pdf", True, id="c.10380 raw non-ASCII text in a B word"),
    pytest.param("=?utf-8?q?日本.exe?=", False, id="c.10380 raw non-ASCII text, other extension"),
    pytest.param("utf-8''\ud800", False, id="lone surrogate in an rfc 2231 value"),
]


@pytest.mark.parametrize(("filename", "expected"), ENCODED_NAME_ROWS)
def test_an_octet_stream_part_is_judged_on_the_decoded_name(filename: str, expected: bool) -> None:
    assert is_pdf_part(part(OCTET, filename)) is expected


@pytest.mark.parametrize(
    "filename",
    [row[0] for row in DECODE_ROWS]
    + [
        "=?utf-8?q?" * 50,
        "'" * 10,
        "''",
        "'a'",
        "\x00",
        "=?\x00?q?\x00?=",
        "%" * 20,
        "%zz",
        "=?utf-8?q?日本.pdf?=",
        "=?utf-8?b?éééé?=.pdf",
    ],
)
def test_no_name_makes_the_rule_raise(filename: str) -> None:
    assert isinstance(is_pdf_part(part(OCTET, filename)), bool)
    assert isinstance(is_pdf_part(part(PDF, filename)), bool)


# ------------------------------------------------------------------ bounds: cap and charset list
# The 59 charsets the product-owner confirmed (PGD-18 c.10394, F0), in the matching form. The
# tests pin this exact list: adding a spelling is a product decision, not an edit.
PO_CHARSETS = (
    "utf-8",
    "utf8",
    "us-ascii",
    "ascii",
    "latin1",
    "latin-1",
    "iso8859-1",
    "iso-8859-1",
    "iso-8859-2",
    "iso-8859-3",
    "iso-8859-4",
    "iso-8859-5",
    "iso-8859-6",
    "iso-8859-7",
    "iso-8859-8",
    "iso-8859-9",
    "iso-8859-10",
    "iso-8859-11",
    "iso-8859-13",
    "iso-8859-14",
    "iso-8859-15",
    "iso-8859-16",
    "windows-1250",
    "windows-1251",
    "windows-1252",
    "windows-1253",
    "windows-1254",
    "windows-1255",
    "windows-1256",
    "windows-1257",
    "windows-1258",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "koi8-r",
    "koi8-u",
    "gb2312",
    "gbk",
    "gb18030",
    "big5",
    "big5-hkscs",
    "shift-jis",
    "sjis",
    "cp932",
    "euc-jp",
    "iso-2022-jp",
    "euc-kr",
    "ks-c-5601-1987",
    "iso-2022-kr",
    "tis-620",
    "utf-16",
    "utf-16le",
    "utf-16be",
)
# Codecs that exist in the standard library (or are plausible spellings) but are not listed. The
# first four must stay out for ever: they are slow (punycode) or turn text into escapes.
UNLISTED_CHARSETS = (
    "punycode",
    "idna",
    "unicode_escape",
    "raw_unicode_escape",
    "unicode-escape",
    "utf-7",
    "utf_7",
    "utf-32",
    "utf-8-sig",
    "mbcs",
    "oem",
    "cp437",
    "cp037",
    "cp949",
    "cp950",
    "windows-31j",
    "windows-874",
    "x-sjis",
    "rot13",
    "base64",
    "hex",
    "latin",
    "l1",
    "nosuch",
    "utf-8x",
    "xutf-8",
    "a\x00b",
)
ENCODINGS_CACHE: dict[str, object] = vars(encodings)["_cache"]


@dataclass
class Calls:
    """What the spies saw: names given to ``codecs.lookup``, words given to ``decode_header``."""

    lookups: list[str] = field(default_factory=list)
    words: list[str] = field(default_factory=list)


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> Calls:
    """Spies on ``codecs.lookup`` and on the ``decode_header`` that ``mime`` uses."""
    seen = Calls()
    real_lookup = codecs.lookup
    real_decode_header = mime.decode_header

    def lookup(name: str) -> codecs.CodecInfo:
        seen.lookups.append(name)
        return real_lookup(name)

    def decode_header_spy(value: str) -> list[tuple[Any, Any]]:
        seen.words.append(value)
        return real_decode_header(value)

    monkeypatch.setattr(codecs, "lookup", lookup)
    monkeypatch.setattr(mime, "decode_header", decode_header_spy)
    return seen


def cache_key(charset: str) -> str:
    """The key ``encodings.search_function`` stores a lookup of ``charset`` under."""
    return encodings.normalize_encoding(charset)


def test_the_charset_list_and_the_cap_are_the_confirmed_values() -> None:
    assert len(PO_CHARSETS) == len(set(PO_CHARSETS)) == 59
    assert frozenset(PO_CHARSETS) == mime.LISTED_CHARSETS
    assert mime.MAX_NAME == 4096
    assert not mime.LISTED_CHARSETS & {"punycode", "idna", "unicode_escape", "raw_unicode_escape"}


@pytest.mark.parametrize("charset", PO_CHARSETS)
def test_every_listed_charset_resolves_on_this_python(charset: str) -> None:
    # F0: runs on every CI leg, so the 3.10 and 3.11 legs prove the list there too.
    assert codecs.lookup(charset).name


@pytest.mark.parametrize("charset", PO_CHARSETS)
def test_a_listed_charset_is_decoded_in_both_forms(charset: str, calls: Calls) -> None:
    word = f"=?{charset}?q?a?="
    value = f"{charset}''%41"

    assert decode_part_name(word) != word
    assert decode_part_name(value) != value
    assert calls.words == [word]


@pytest.mark.parametrize("charset", UNLISTED_CHARSETS)
def test_an_unlisted_charset_is_never_looked_up_and_stays_as_received(
    charset: str, calls: Calls, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delitem(ENCODINGS_CACHE, cache_key(charset), raising=False)
    word = f"=?{charset}?q?abc?="
    value = f"{charset}''%41%42"

    assert decode_part_name(word) == word
    assert decode_part_name(value) == value
    assert is_pdf_part(part(OCTET, word)) is False
    assert calls.words == []
    assert calls.lookups == []
    assert cache_key(charset) not in ENCODINGS_CACHE


def test_400_distinct_unlisted_charsets_cause_no_lookup_and_leave_the_codec_cache_alone(
    calls: Calls,
) -> None:
    names = [f"qz{i}x" for i in range(400)]
    assert not any(cache_key(name) in ENCODINGS_CACHE for name in names)
    before = dict(ENCODINGS_CACHE)

    for name in names:
        word = f"=?{name}?q?a?="
        value = f"{name}''%41"
        assert decode_part_name(word) == word
        assert decode_part_name(value) == value

    assert calls.lookups == []
    assert calls.words == []
    assert before == ENCODINGS_CACHE


def test_a_name_filled_with_distinct_unlisted_charsets_is_left_alone(calls: Calls) -> None:
    words: list[str] = []
    size = 0
    while size + len(word := f"=?qy{len(words)}x?q?a?=") <= mime.MAX_NAME:
        words.append(word)
        size += len(word)
    name = "".join(words)
    before = dict(ENCODINGS_CACHE)

    assert mime.MAX_NAME - 20 < len(name) <= mime.MAX_NAME  # under the cap, so it is not skipped
    assert len(words) >= 300
    assert decode_part_name(name) == name
    assert calls.lookups == []
    assert calls.words == []
    assert before == ENCODINGS_CACHE


def test_each_listed_word_reaches_decode_header_once_and_no_codec_lookup_is_made(
    calls: Calls,
) -> None:
    name = "=?utf-8?q?a?= =?LATIN_1?q?b?= =?cp1252*en?q?c?= =?nosuch?q?d?="

    assert decode_part_name(name) == "abc=?nosuch?q?d?="
    assert calls.words == ["=?utf-8?q?a?=", "=?LATIN_1?q?b?=", "=?cp1252*en?q?c?="]
    assert calls.lookups == []


def test_a_listed_charset_that_this_runtime_lacks_is_kept_as_received(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A stripped (frozen) build may lack a listed codec; the fragment must not raise.
    monkeypatch.setattr(mime, "LISTED_CHARSETS", mime.LISTED_CHARSETS | {"nosuch"})
    word = "=?nosuch?q?a.pdf?="
    value = "nosuch''%41.pdf"

    assert decode_part_name(word) == word
    assert decode_part_name(value) == value


def _filled(prefix: str, suffix: str, size: int) -> str:
    return prefix + "a" * (size - len(prefix) - len(suffix)) + suffix


def test_a_name_of_exactly_the_cap_is_decoded(calls: Calls) -> None:
    name = _filled("=?utf-8?q?", "?=", mime.MAX_NAME)

    assert len(name) == mime.MAX_NAME
    assert decode_part_name(name) == "a" * (mime.MAX_NAME - 12)
    assert calls.words == [name]


def test_a_name_one_over_the_cap_is_returned_as_received(calls: Calls) -> None:
    name = _filled("=?utf-8?q?", "?=", mime.MAX_NAME + 1)

    assert decode_part_name(name) == name
    assert calls.words == []


def test_the_cap_counts_the_name_as_received_before_white_space_is_stripped() -> None:
    padded = _filled("=?utf-8?q?", "?= ", mime.MAX_NAME + 1)
    value = _filled("utf-8''", " ", mime.MAX_NAME + 1)

    assert decode_part_name(padded) == padded
    assert decode_part_name(value) == value


def test_nothing_runs_on_a_name_over_the_cap(calls: Calls, monkeypatch: pytest.MonkeyPatch) -> None:
    class Forbidden:
        def __getattr__(self, name: str) -> None:
            raise AssertionError(f"a pattern was used on a name over the cap: {name}")

    monkeypatch.setattr(mime, "_ENCODED_WORD", Forbidden())
    monkeypatch.setattr(mime, "_EXTENDED_VALUE", Forbidden())
    big = mime.MAX_NAME + 1

    for name in (_filled("=?utf-8?q?", "?=", big), _filled("utf-8''", "", big), "=?a?q?" * big):
        assert decode_part_name(name) == name
    assert calls.words == []
    assert calls.lookups == []


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        pytest.param("a" * 5_000 + ".pdf", True, id="plain name over the cap, .pdf"),
        pytest.param("a" * 5_000 + ".exe", False, id="plain name over the cap, .exe"),
        pytest.param(" " * 5_000 + "a.pdf", True, id="white space then .pdf over the cap"),
        pytest.param(_filled("=?utf-8?q?", ".pdf?=", 5_000), False, id="encoded name over the cap"),
        pytest.param(_filled("utf-8''", "%2Epdf", 5_000), False, id="rfc 2231 name over the cap"),
        pytest.param(_filled("utf-8''", ".pdf", 5_000), True, id="rfc 2231 plain end over the cap"),
        pytest.param(_filled("=?utf-8?q?", ".pdf?=", 100), True, id="encoded name under the cap"),
    ],
)
def test_a_name_over_the_cap_takes_the_ordinary_test_on_the_text_as_received(
    filename: str, expected: bool
) -> None:
    assert is_pdf_part(part(OCTET, filename)) is expected


# ------------------------------------------------------------------ time: perf marker only
def _every_listed_charset_in_one_name() -> str:
    words: list[str] = []
    while sum(map(len, words)) < mime.MAX_NAME - 40:
        charset = PO_CHARSETS[len(words) % len(PO_CHARSETS)]
        words.append(f"=?{charset}?q?a?=")
    return "".join(words)


HOSTILE_NAMES = {
    "listed charsets cycled, at the cap": _every_listed_charset_in_one_name,
    "punycode, 1 MB": lambda: "punycode''" + "a" * 1_000_000,
    "unfinished words, 1 MB": lambda: "=?x?q?a?=" * 110_000,
    "base64 words, 1 MB": lambda: "=?utf-8?b?QQ==?=" * 60_000,
    "plain, 1 MB": lambda: "a" * 1_000_000 + ".pdf",
}


@pytest.mark.perf
@pytest.mark.parametrize("shape", list(HOSTILE_NAMES))
def test_a_hostile_name_is_judged_well_inside_the_per_message_budget(shape: str) -> None:
    # NFR-003 gives 50 ms per message; 0.25 s is five times that, to stay clear of CI noise. The
    # first call warms the codec imports (a cost paid once per process); counts, not time, are
    # what the rest of the suite pins.
    name = HOSTILE_NAMES[shape]()
    is_pdf_part(part(OCTET, name))

    started = time.perf_counter()
    is_pdf_part(part(OCTET, name))

    assert time.perf_counter() - started < 0.25
