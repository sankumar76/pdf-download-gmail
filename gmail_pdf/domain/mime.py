"""Which message parts are PDFs (FR-019, BR-008, EC-04; architecture 4.1 and 6.6 step 2).

Pure functions on part metadata: no I/O, no logging and no text of their own. A name is never
echoed, so there is no text surface here (NFR-016, NFR-012); the body of a part is not an
input at all. Walking the part tree, ``message/rfc822`` and naming belong to other stories.
"""

from __future__ import annotations

import re
from email.errors import HeaderParseError
from email.header import decode_header
from urllib.parse import unquote

from gmail_pdf.domain.models import PartInfo

PDF_MIME_TYPE = "application/pdf"
OCTET_STREAM_MIME_TYPE = "application/octet-stream"
PDF_SUFFIX = ".pdf"

# A name longer than this (``len`` of the string as received) is never decoded: the work is
# bounded before any pattern or codec runs (PERF-21, PERF-22). The longest legitimate name,
# 255 characters in 4-byte text as RFC 2047 words, is about 3,730 characters (F0, c.10394).
MAX_NAME = 4096
# The only charsets a name is decoded with, in their matching form (see ``_charset_key``). A
# charset outside this set is never looked up: a lookup of an unseen name costs a failed import
# and a permanent ``encodings._cache`` entry (PERF-26), and ``punycode`` is quadratic (PERF-21).
# ``punycode``, ``idna``, ``unicode_escape`` and ``raw_unicode_escape`` must stay out.
LISTED_CHARSETS = frozenset(
    {
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
    }
)

# One RFC 2047 encoded word: =?charset?q-or-b?text?= . Same shape as the one in
# ``email.header``, but without white space, so a word can be handed to ``decode_header`` alone.
_ENCODED_WORD = re.compile(r"=\?([^?\s]+)\?[qQbB]\?[^?\s]*\?=")
# An RFC 2231 value: charset'language'percent-encoded-text (the charset is never empty here).
_EXTENDED_VALUE = re.compile(r"([^\s'*]+)'[^\s']*'(.*)", re.DOTALL)


def normalise_content_type(value: str) -> str:
    """Return the media type of a ``Content-Type`` value: lower case, parameters removed.

    >>> normalise_content_type('Application/PDF; name="a.pdf"')
    'application/pdf'
    """
    return value.partition(";")[0].strip().lower()


def decode_part_name(name: str) -> str:
    """Decode an RFC 2047 or RFC 2231 encoded file name; never raises, never logs.

    A name of the shape ``charset'language'text`` whose charset is in ``LISTED_CHARSETS`` is read
    as an RFC 2231 value, and any other name as RFC 2047 words, so an ordinary name of that shape
    is rewritten too: ``latin1'draft'report.pdf`` gives ``report.pdf`` (detection is not
    affected, since the suffix survives; naming decides whether to keep the rewrite). Only the
    ``%XX`` runs of an RFC 2231 value are decoded with its charset.

    An encoded word in a listed charset is always decoded, whatever its text holds: bytes that
    are invalid in the charset become U+FFFD, and raw non-ASCII text (``=?utf-8?q?`` followed
    by Japanese characters, say) is decoded as the standard library does, so a name that ends
    in ``.pdf`` keeps that ending and is a PDF (PGD-18 c.10380: losing a real PDF is the worse
    error). Tests pin the verdict for such words, not their text.

    Only a fragment that cannot be decoded at all is kept exactly as received, and the rest of
    the name is still decoded: a charset not in the list (it is never looked up), bad base64,
    an unfinished word. A name longer than ``MAX_NAME`` characters is returned as received,
    undecoded. Any other name is returned unchanged.

    Args:
        name: A part's ``filename``, possibly holding encoded words or an RFC 2231 value
            (``charset'language'percent-text``).

    Returns:
        The decoded name. White space around an RFC 2231 value is dropped with the value; the
        text of an RFC 2047 name keeps its own white space.
    """
    if len(name) > MAX_NAME:  # counted as received, before any pattern or codec runs
        return name
    # Surrounding white space is not part of an RFC 2231 value, so it cannot change the reading.
    extended = _EXTENDED_VALUE.fullmatch(name.strip())
    if extended is not None:
        decoded = _decode_extended(*extended.groups())
        if decoded is not None:
            return decoded
    # Not an RFC 2231 value, or one that cannot be decoded: an RFC 2047 word can hold two
    # apostrophes (``=?utf-8?q?O'Brien's.pdf?=``), so the name is still read as encoded words.
    return _decode_encoded_words(name)


def is_pdf_part(part: PartInfo) -> bool:
    """Say whether a part is a PDF, from its type and file name only (FR-019, BR-008).

    A PDF is ``application/pdf`` (any name, an empty one too), or ``application/octet-stream``
    whose decoded name, stripped of surrounding white space, ends in ``.pdf`` in any case. The
    body is never looked at. A change to this rule increments ``detector_version`` (architecture
    5.4); that constant arrives with the manifest.

    Args:
        part: The part's metadata.

    Returns:
        True for a PDF part.
    """
    mime_type = normalise_content_type(part.mime_type)
    if mime_type == PDF_MIME_TYPE:
        return True
    return mime_type == OCTET_STREAM_MIME_TYPE and _has_pdf_name(part.filename)


def _has_pdf_name(filename: str) -> bool:
    return decode_part_name(filename).strip().lower().endswith(PDF_SUFFIX)


def _decode_encoded_words(name: str) -> str:
    """Decode every RFC 2047 word in ``name``; white space between two words is dropped."""
    pieces: list[str] = []
    position = 0
    after_word = False
    for match in _ENCODED_WORD.finditer(name):
        gap = name[position : match.start()]
        if not (after_word and gap.isspace()):
            pieces.append(gap)
        pieces.append(_decode_word(match))
        position = match.end()
        after_word = True
    pieces.append(name[position:])
    return "".join(pieces)


def _decode_word(match: re.Match[str]) -> str:
    """Decode one encoded word, or return it as received if it cannot be decoded."""
    word = match.group()
    charset = _charset_key(match.group(1))
    if charset not in LISTED_CHARSETS:  # never reaches ``decode_header`` or a codec lookup
        return word
    try:
        ((payload, _),) = decode_header(word)
    except HeaderParseError:  # bad base64
        return word
    decoded = _decode_bytes(payload, charset)
    return word if decoded is None else decoded


def _decode_extended(charset: str, escaped: str) -> str | None:
    """Decode the percent-encoded part of an RFC 2231 value; None if that is not possible."""
    key = _charset_key(charset)
    if key not in LISTED_CHARSETS:  # never reaches a codec lookup
        return None
    try:
        # Only the ``%XX`` runs are decoded with the charset; other text passes through as it is.
        return unquote(escaped, encoding=key, errors="replace")
    except LookupError:  # a listed codec that this runtime lacks
        return None


def _charset_key(charset: str) -> str:
    """The form in which a charset is matched against ``LISTED_CHARSETS``.

    A language tag after the charset (RFC 2231 section 5: ``utf-8*en``) is removed, the rest is
    lower-cased and ``_`` is read as ``-``.
    """
    return charset.partition("*")[0].lower().replace("_", "-")


def _decode_bytes(data: bytes, charset: str) -> str | None:
    """``data`` decoded with a listed ``charset`` (bad bytes replaced); None if it is missing.

    Every listed name resolves on the supported Pythons; a runtime that lacks a codec (a
    stripped, frozen build) raises ``LookupError``, and the fragment is then kept as received.
    """
    try:
        return data.decode(charset, errors="replace")
    except LookupError:
        return None
