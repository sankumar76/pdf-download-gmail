"""In-memory Gmail mailbox implementing ``GmailPort`` (test-strategy sections 2, 3 and 10).

Capabilities (AC-7):

* configurable page size with opaque page tokens, and shuffled list order (FR-014);
* Gmail-shaped message resources with nested ``multipart/*`` and ``message/rfc822`` parts,
  small bodies inline (``body.data``) or large ones behind an ``attachmentId``;
* scripted per-call faults (HTTP 429/5xx/403-rate-limit, 400/404, timeout) and latency;
* a switchable inclusive/exclusive reading of epoch ``after:`` / ``before:`` terms (AA-01);
* a call recorder (method, params) for NFR-011 assertions.

Supported query terms: ``has:attachment``, ``filename:<ext-or-name>``, ``after:<epoch s>``,
``before:<epoch s>``, each optionally negated with ``-``, and plain words (matched against
the Subject header). Any other ``key:value`` term, ``OR``/``AND``, ``{}``/``()`` grouping and
quoted phrases raise ``UnsupportedQueryError`` rather than being silently ignored. JSON
persistence lives in ``tests/fakes/fake_gmail_json.py``. All content is synthetic (``example.com``).
"""

from __future__ import annotations

# Over 400 lines on purpose (STD-56): the fake and its query terms are one unit, and the module
# docstring above is the whole contract; a split would put the rules away from the class.
import base64
import copy
import random
import time
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType

from gmail_pdf.app.ports import JsonObject, MessageIdPage

WILDCARD_METHOD = "*"
SPAM_TRASH_LABELS = frozenset({"SPAM", "TRASH"})


# Gmail's documented ceiling for ``maxResults`` on ``users.messages.list``.
DEFAULT_PAGE_SIZE = 500
# Query grouping syntax Gmail supports but the fake does not.
_UNSUPPORTED_BOOLEAN_WORDS = frozenset({"OR", "AND"})
_GROUP_OPENERS = '{("'
_GROUP_CLOSERS = '})"'


class EpochBounds(Enum):
    """How ``after:N`` / ``before:N`` treat a message received exactly at second N."""

    INCLUSIVE = "inclusive"  # after:N keeps s >= N, before:N keeps s <= N
    EXCLUSIVE = "exclusive"  # after:N keeps s > N, before:N keeps s < N


DEFAULT_EPOCH_BOUNDS = EpochBounds.INCLUSIVE


class UnsupportedQueryError(ValueError):
    """The fake does not implement this Gmail search term."""


class FakeGmailHttpError(Exception):
    """Scripted Gmail HTTP failure (status, reason, optional ``Retry-After`` seconds)."""

    def __init__(self, status: int, reason: str = "", *, retry_after: float | None = None) -> None:
        super().__init__(f"HTTP {status} {reason}".strip())
        self.status = status
        self.reason = reason
        self.retry_after = retry_after


class FakeGmailTimeout(TimeoutError):
    """Scripted network timeout."""


@dataclass(frozen=True, slots=True)
class Call:
    """One recorded call to the fake."""

    method: str
    params: Mapping[str, object]
    faulted: bool = False


@dataclass(frozen=True, slots=True)
class FakeMessage:
    """A message resource (``format=full``) plus the bytes behind its ``attachmentId`` bodies."""

    resource: JsonObject
    attachments: Mapping[str, bytes] = field(default_factory=dict)

    @property
    def message_id(self) -> str:
        """The Gmail message id."""
        return str(self.resource["id"])

    @property
    def internal_seconds(self) -> int:
        """``internalDate`` in whole epoch seconds."""
        return int(self.resource["internalDate"]) // 1000


@dataclass(frozen=True, slots=True)
class _Cursor:
    """One paged listing: the search it belongs to and the ids it returns, page by page."""

    query: str
    include_spam_trash: bool
    ids: list[str]


@dataclass(slots=True)
class _ScriptedFault:
    method: str
    factory: Callable[[], Exception]
    remaining: int | None
    skip: int
    match: dict[str, object]


def b64url_encode(data: bytes) -> str:
    """Base64url without padding, as Gmail returns ``body.data``."""
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def b64url_decode(text: str) -> bytes:
    """Decode base64url, restoring the padding."""
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def iter_parts(part: Mapping[str, object]) -> Iterator[Mapping[str, object]]:
    """Yield ``part`` and every nested part in document order."""
    yield part
    children = part.get("parts")
    if isinstance(children, list):
        for child in children:
            yield from iter_parts(child)


def _has_attachment(message: FakeMessage) -> bool:
    for part in iter_parts(message.resource["payload"]):
        body = part.get("body")
        if part.get("filename") or (isinstance(body, dict) and body.get("attachmentId")):
            return True
    return False


def _has_filename(message: FakeMessage, wanted: str) -> bool:
    needle = wanted.casefold()
    for part in iter_parts(message.resource["payload"]):
        name = str(part.get("filename") or "").casefold()
        if name and (name == needle or name.endswith("." + needle)):
            return True
    return False


def _subject(message: FakeMessage) -> str:
    for header in message.resource["payload"].get("headers", []):
        if str(header.get("name", "")).lower() == "subject":
            return str(header.get("value", ""))
    return ""


def _negated(predicate: Callable[[FakeMessage], bool]) -> Callable[[FakeMessage], bool]:
    return lambda message: not predicate(message)


class FakeGmail:
    """Fake mailbox; construct, ``add`` messages, hand it to code expecting a ``GmailPort``."""

    def __init__(
        self,
        messages: Iterable[FakeMessage] = (),
        *,
        page_size: int = DEFAULT_PAGE_SIZE,
        shuffle_seed: int | None = None,
        latency_s: float = 0.0,
        epoch_bounds: EpochBounds = DEFAULT_EPOCH_BOUNDS,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if page_size < 1:
            raise ValueError("page_size must be at least 1")
        self.page_size = page_size
        self.latency_s = latency_s
        self.epoch_bounds = epoch_bounds
        self.calls: list[Call] = []
        self._shuffle_seed = shuffle_seed
        self._rng = random.Random(shuffle_seed) if shuffle_seed is not None else None
        self._sleep = sleep
        self._messages: dict[str, FakeMessage] = {}
        self._faults: list[_ScriptedFault] = []
        self._cursors: dict[str, _Cursor] = {}
        for message in messages:
            self.add(message)

    # ------------------------------------------------------------------ mailbox content
    def add(self, message: FakeMessage) -> None:
        """Add a message; a duplicate id is a test bug."""
        if message.message_id in self._messages:
            raise ValueError(f"duplicate message id {message.message_id!r}")
        self._messages[message.message_id] = message

    @property
    def message_ids(self) -> list[str]:
        """Ids in insertion order (not list order)."""
        return list(self._messages)

    @property
    def messages(self) -> list[FakeMessage]:
        """Messages in insertion order."""
        return list(self._messages.values())

    @property
    def shuffle_seed(self) -> int | None:
        """Seed of the list-order shuffle, or ``None`` for newest-first order."""
        return self._shuffle_seed

    # ------------------------------------------------------------------ fault scripting
    def fail_with_http(
        self,
        method: str,
        status: int,
        reason: str = "",
        *,
        times: int | None = 1,
        skip: int = 0,
        retry_after: float | None = None,
        **match: object,
    ) -> None:
        """Make matching calls to ``method`` raise ``FakeGmailHttpError``.

        Args:
            method: ``list_message_ids``, ``get_message``, ``get_attachment`` or ``"*"``.
            status: HTTP status, e.g. 429, 500, 503, 403, 400, 404.
            reason: Gmail error reason, e.g. ``rateLimitExceeded``.
            times: How many matching calls fail; ``None`` means every one.
            skip: Matching calls that succeed before the faults start.
            retry_after: Seconds for a ``Retry-After`` header, if any.
            **match: Parameter values a call must have (e.g. ``message_id="m3"``).
        """

        def factory() -> Exception:
            return FakeGmailHttpError(status, reason, retry_after=retry_after)

        self._script(method, factory, times, skip, match)

    def fail_with_timeout(
        self, method: str, *, times: int | None = 1, skip: int = 0, **match: object
    ) -> None:
        """Make matching calls raise ``FakeGmailTimeout`` (same arguments as above)."""
        self._script(method, lambda: FakeGmailTimeout("scripted timeout"), times, skip, match)

    def _script(
        self,
        method: str,
        factory: Callable[[], Exception],
        times: int | None,
        skip: int,
        match: dict[str, object],
    ) -> None:
        if times is not None and times < 1:
            raise ValueError("times must be at least 1, or None for every matching call")
        if skip < 0:
            raise ValueError("skip must not be negative")
        self._faults.append(_ScriptedFault(method, factory, times, skip, dict(match)))

    def _take_fault(self, method: str, params: Mapping[str, object]) -> _ScriptedFault | None:
        for fault in self._faults:
            if fault.method not in (method, WILDCARD_METHOD):
                continue
            if any(params.get(key) != value for key, value in fault.match.items()):
                continue
            if fault.skip > 0:
                fault.skip -= 1
                continue
            if fault.remaining is not None:
                fault.remaining -= 1
                if fault.remaining <= 0:
                    self._faults.remove(fault)
            return fault
        return None

    def _begin(self, method: str, params: Mapping[str, object]) -> None:
        """Apply latency, record the call, and raise the scripted fault if one is due."""
        if self.latency_s > 0:
            self._sleep(self.latency_s)
        fault = self._take_fault(method, params)
        self.calls.append(Call(method, MappingProxyType(dict(params)), fault is not None))
        if fault is not None:
            raise fault.factory()

    def calls_to(self, method: str) -> list[Call]:
        """Recorded calls to one method."""
        return [call for call in self.calls if call.method == method]

    # ------------------------------------------------------------------ GmailPort
    def list_message_ids(
        self,
        query: str,
        *,
        page_token: str | None = None,
        include_spam_trash: bool = False,
    ) -> MessageIdPage:
        """List one page of ids matching ``query`` (see the module docstring for terms)."""
        self._begin(
            "list_message_ids",
            {"query": query, "page_token": page_token, "include_spam_trash": include_spam_trash},
        )
        if page_token is None:
            cursor = f"cursor-{len(self._cursors)}"
            ids = self._matching_ids(query, include_spam_trash)
            self._cursors[cursor] = _Cursor(query, include_spam_trash, ids)
            offset = 0
        else:
            # Gmail rejects a token used with another query or spam flag (QUA-03, #11), so a
            # token mix-up between the two paged searches of ADR-007 fails here as well.
            cursor, offset = self._parse_token(page_token, query, include_spam_trash)
            ids = self._cursors[cursor].ids
        page = ids[offset : offset + self.page_size]
        end = offset + len(page)
        return MessageIdPage(tuple(page), f"{cursor}:{end}" if end < len(ids) else None)

    def get_message(self, message_id: str) -> JsonObject:
        """Return a copy of the ``format=full`` resource; 404 if unknown."""
        self._begin("get_message", {"message_id": message_id})
        return copy.deepcopy(self._find(message_id).resource)

    def get_attachment(self, message_id: str, attachment_id: str) -> bytes:
        """Return the bytes behind ``attachment_id``; 404 if message or id is unknown."""
        self._begin("get_attachment", {"message_id": message_id, "attachment_id": attachment_id})
        message = self._find(message_id)
        if attachment_id not in message.attachments:
            raise FakeGmailHttpError(404, "notFound")
        return message.attachments[attachment_id]

    # ------------------------------------------------------------------ internals
    def _find(self, message_id: str) -> FakeMessage:
        if message_id not in self._messages:
            raise FakeGmailHttpError(404, "notFound")
        return self._messages[message_id]

    def _parse_token(self, token: str, query: str, include_spam_trash: bool) -> tuple[str, int]:
        cursor, _, offset_text = token.rpartition(":")
        # ``isdecimal`` alone accepts non-ASCII digits that ``int`` reads as numbers;
        # ``isdigit`` alone accepts superscripts that ``int`` rejects (#15 b): need both.
        if cursor not in self._cursors or not (offset_text.isascii() and offset_text.isdecimal()):
            raise FakeGmailHttpError(400, "invalidPageToken")
        issued = self._cursors[cursor]
        if (issued.query, issued.include_spam_trash) != (query, include_spam_trash):
            raise FakeGmailHttpError(400, "invalidPageToken")
        return cursor, int(offset_text)

    def _matching_ids(self, query: str, include_spam_trash: bool) -> list[str]:
        matches = self._compile(query)
        selected = [
            message
            for message in self._messages.values()
            if (
                include_spam_trash
                or not SPAM_TRASH_LABELS & set(message.resource.get("labelIds", []))
            )
            and matches(message)
        ]
        selected.sort(key=lambda m: (-m.internal_seconds, m.message_id))  # Gmail: newest first
        ids = [message.message_id for message in selected]
        if self._rng is not None:
            self._rng.shuffle(ids)
        return ids

    def _compile(self, query: str) -> Callable[[FakeMessage], bool]:
        predicates: list[Callable[[FakeMessage], bool]] = []
        for raw in query.split():
            negate = raw.startswith("-") and len(raw) > 1
            predicate = self._term(raw[1:] if negate else raw)
            predicates.append(_negated(predicate) if negate else predicate)
        return lambda message: all(predicate(message) for predicate in predicates)

    def _term(self, term: str) -> Callable[[FakeMessage], bool]:
        if (
            term in _UNSUPPORTED_BOOLEAN_WORDS
            or term[0] in _GROUP_OPENERS
            or term[-1] in _GROUP_CLOSERS
        ):
            raise UnsupportedQueryError(f"unsupported search syntax {term!r}")
        key, separator, value = term.partition(":")
        if not separator:
            word = term.casefold()
            return lambda message: word in _subject(message).casefold()
        if key == "has" and value == "attachment":
            return _has_attachment
        if key == "filename" and value:
            return lambda message: _has_filename(message, value)
        if key in ("after", "before") and value.isascii() and value.isdecimal():
            return self._epoch_term(key, int(value))
        raise UnsupportedQueryError(f"unsupported search term {term!r}")

    def _epoch_term(self, key: str, epoch_s: int) -> Callable[[FakeMessage], bool]:
        inclusive = self.epoch_bounds is EpochBounds.INCLUSIVE

        def after(message: FakeMessage) -> bool:
            seconds = message.internal_seconds
            return seconds >= epoch_s if inclusive else seconds > epoch_s

        def before(message: FakeMessage) -> bool:
            seconds = message.internal_seconds
            return seconds <= epoch_s if inclusive else seconds < epoch_s

        return after if key == "after" else before
