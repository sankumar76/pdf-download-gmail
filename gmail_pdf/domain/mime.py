"""Which message parts are PDFs (FR-019, BR-008, EC-04; architecture 4.1 and 6.6 step 2).

Pure functions on part metadata: no I/O, no logging and no text of their own. A name is never
echoed, so there is no text surface here (NFR-016, NFR-012); the body of a part is not an
input at all. Walking the part tree, ``message/rfc822`` and naming belong to other stories.
"""

from __future__ import annotations

import codecs
import re
from email.errors import HeaderParseError
from email.header import decode_header
from urllib.parse import unquote_to_bytes

from gmail_pdf.domain.models import PartInfo

PDF_MIME_TYPE = "application/pdf"
OCTET_STREAM_MIME_TYPE = "application/octet-stream"
PDF_SUFFIX = ".pdf"

# One RFC 2047 encoded word: =?charset?q-or-b?text?= . Same shape as the one in
# ``email.header``, but without white space, so a word can be handed to ``decode_header`` alone.
_ENCODED_WORD = re.compile(r"=\?([^?\s]+)\?[qQbB]\?[^?\s]*\?=")
# An RFC 2231 value: charset'language'percent-encoded-text (the charset is never empty here).
_EXTENDED_VALUE = re.compile(r"([^\s'*]+)'[^\s']*'(.*)", re.DOTALL)
# What can go wrong turning bytes into text: an unknown or non-text charset (LookupError), a
# NUL or a lone surrogate in the input, a codec that refuses ``errors="replace"`` (ValueError).
_DECODE_ERRORS = (LookupError, ValueError)


def normalise_content_type(value: str) -> str:
    """Return the media type of a ``Content-Type`` value: lower case, parameters removed.

    >>> normalise_content_type('Application/PDF; name="a.pdf"')
    'application/pdf'
    """
    return value.partition(";")[0].strip().lower()


def decode_part_name(name: str) -> str:
    """Decode an RFC 2047 or RFC 2231 encoded file name; never raises, never logs.

    Bytes that are invalid in their charset become U+FFFD. A fragment that cannot be decoded
    (unknown charset, bad base64, unfinished word) is kept exactly as received, and the rest of
    the name is still decoded. A name with no encoding is returned unchanged.

    Args:
        name: A part's ``filename``, possibly holding encoded words or an RFC 2231 value
            (``charset'language'percent-text``).

    Returns:
        The decoded name. White space around an RFC 2231 value is dropped with the value; the
        text of an RFC 2047 name keeps its own white space.
    """
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
        pieces.append(_decode_word(match.group()))
        position = match.end()
        after_word = True
    pieces.append(name[position:])
    return "".join(pieces)


def _decode_word(word: str) -> str:
    """Decode one encoded word, or return it as received if it cannot be decoded."""
    try:
        ((payload, charset),) = decode_header(word)
    except HeaderParseError:  # bad base64
        return word
    # RFC 2231 section 5 allows a language tag after the charset: ``utf-8*en``. The charset is
    # never None for a word matched above; ``or ""`` only satisfies the type checker.
    decoded = _decode_bytes(payload, (charset or "").partition("*")[0])
    return word if decoded is None else decoded


def _decode_extended(charset: str, escaped: str) -> str | None:
    """Decode the percent-encoded part of an RFC 2231 value; None if that is not possible."""
    try:
        return _decode_bytes(unquote_to_bytes(escaped), charset)
    except ValueError:  # a lone surrogate cannot be turned into bytes
        return None


def _decode_bytes(data: bytes, charset: str) -> str | None:
    """``data`` decoded with ``charset`` (bad bytes replaced); None if the charset is unusable."""
    try:
        codecs.lookup(charset)
        return data.decode(charset, errors="replace")
    except _DECODE_ERRORS:
        return None
