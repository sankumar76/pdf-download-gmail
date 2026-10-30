"""Builders for synthetic Gmail messages (test-strategy section 3, AC-7).

Example::

    message = (
        MessageBuilder("m1")
        .received("2026-01-15T23:59:59", "America/New_York")
        .pdf("Invoice.pdf")
        .forwarded(MessageBuilder().pdf("Inner.pdf"))
        .build()
    )

The result is a ``FakeMessage``: a Gmail ``format=full`` resource plus the bytes behind each
``attachmentId``. All content is synthetic: addresses use ``example.com`` (CLAUDE.md section 6.7).
"""

from __future__ import annotations

import copy
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from zoneinfo import ZoneInfo

from gmail_pdf.app.ports import JsonObject
from tests.fakes.fake_gmail import FakeMessage, b64url_encode

DEFAULT_SENDER = "sender@example.com"
DEFAULT_RECIPIENT = "recipient@example.com"
PDF_HEADER = b"%PDF-1.4\n"
PDF_TRAILER = b"\n%%EOF\n"
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_ONE_MS = timedelta(milliseconds=1)


def make_pdf_bytes(size: int = 256, label: str = "") -> bytes:
    """Return ``size`` bytes that start with ``%PDF-`` and end with ``%%EOF`` (synthetic)."""
    minimum = len(PDF_HEADER) + len(PDF_TRAILER)
    if size < minimum:
        raise ValueError(f"a synthetic PDF needs at least {minimum} bytes")
    filler = (label.encode("utf-8") + b" ").ljust(size - minimum, b"%")[: size - minimum]
    return PDF_HEADER + filler + PDF_TRAILER


def epoch_ms(local_iso: str, tz: str = "UTC", *, fold: int = 0) -> int:
    """Convert a wall-clock time in an IANA zone to epoch milliseconds.

    Args:
        local_iso: ``YYYY-MM-DDTHH:MM:SS`` wall-clock time.
        tz: IANA zone name.
        fold: ``1`` selects the second occurrence of an ambiguous time (DST fall-back).
    """
    moment = datetime.fromisoformat(local_iso).replace(tzinfo=ZoneInfo(tz), fold=fold)
    return (moment - _EPOCH) // _ONE_MS


@dataclass(slots=True)
class _Node:
    mime_type: str
    filename: str = ""
    headers: list[tuple[str, str]] = field(default_factory=list)
    inline: bytes | None = None
    attachment: bytes | None = None
    children: list[_Node] = field(default_factory=list)


class MessageBuilder:
    """Fluent builder for one message."""

    def __init__(self, message_id: str | None = None) -> None:
        self.message_id = message_id
        self._internal_ms = epoch_ms("2026-01-15T12:00:00")
        self._sender = DEFAULT_SENDER
        self._subject = "Synthetic message"
        self._labels: list[str] = ["INBOX"]
        self._root = _Node("multipart/mixed")
        self._stack: list[_Node] = [self._root]

    # ------------------------------------------------------------------ envelope
    def received(self, local_iso: str, tz: str = "UTC", *, fold: int = 0) -> MessageBuilder:
        """Set ``internalDate`` from a wall-clock time in ``tz``."""
        self._internal_ms = epoch_ms(local_iso, tz, fold=fold)
        return self

    def received_epoch_ms(self, internal_ms: int) -> MessageBuilder:
        """Set ``internalDate`` directly (epoch milliseconds)."""
        self._internal_ms = internal_ms
        return self

    def sender(self, address: str) -> MessageBuilder:
        """Set the From address."""
        self._sender = address
        return self

    def subject(self, text: str) -> MessageBuilder:
        """Set the Subject header."""
        self._subject = text
        return self

    def labels(self, *labels: str) -> MessageBuilder:
        """Replace the label ids (e.g. ``"SPAM"``)."""
        self._labels = list(labels)
        return self

    # ------------------------------------------------------------------ parts
    def text(self, body: str = "Synthetic body text.") -> MessageBuilder:
        """Add an inline ``text/plain`` part."""
        self._add(_Node("text/plain", inline=body.encode("utf-8")))
        return self

    def pdf(
        self, filename: str | None, *, content: bytes | None = None, inline: bool = False
    ) -> MessageBuilder:
        """Add an ``application/pdf`` part; ``None`` means a part with no file name."""
        data = content if content is not None else make_pdf_bytes(label=filename or "unnamed")
        return self.attachment(filename, "application/pdf", data, inline=inline)

    def attachment(
        self, filename: str | None, mime_type: str, content: bytes, *, inline: bool = False
    ) -> MessageBuilder:
        """Add a file part. ``inline=True`` puts the bytes in ``body.data``; otherwise they sit
        behind an ``attachmentId`` and are served by ``get_attachment``."""
        node = _Node(mime_type, filename=filename or "")
        if inline:
            node.inline = content
        else:
            node.attachment = content
        self._add(node)
        return self

    @contextmanager
    def multipart(self, subtype: str = "mixed") -> Iterator[MessageBuilder]:
        """Nest the parts added inside the ``with`` block in a ``multipart/<subtype>`` part."""
        container = _Node(f"multipart/{subtype}")
        self._add(container)
        self._stack.append(container)
        try:
            yield self
        finally:
            self._stack.pop()

    def forwarded(self, inner: MessageBuilder, filename: str = "") -> MessageBuilder:
        """Add a ``message/rfc822`` part that carries ``inner`` as an attached message."""
        wrapper = _Node("message/rfc822", filename=filename)
        wrapper.children.append(inner._envelope_root())
        self._add(wrapper)
        return self

    def _add(self, node: _Node) -> None:
        self._stack[-1].children.append(node)

    # ------------------------------------------------------------------ output
    def _envelope_root(self) -> _Node:
        root = copy.deepcopy(self._root)
        root.headers = [
            ("From", self._sender),
            ("To", DEFAULT_RECIPIENT),
            ("Subject", self._subject),
            ("Date", format_datetime(_EPOCH + self._internal_ms * _ONE_MS)),
        ]
        return root

    def build(self, message_id: str | None = None) -> FakeMessage:
        """Produce the message resource and its attachment bytes."""
        resolved = message_id or self.message_id
        if resolved is None:
            raise ValueError("a message id is required (constructor, build() or build_messages)")
        attachments: dict[str, bytes] = {}
        payload = _render(self._envelope_root(), "", resolved, attachments)
        resource: JsonObject = {
            "id": resolved,
            "threadId": f"thread-{resolved}",
            "labelIds": list(self._labels),
            "internalDate": str(self._internal_ms),
            "sizeEstimate": sum(len(data) for data in attachments.values()),
            "snippet": "",
            "payload": payload,
        }
        return FakeMessage(resource, attachments)


def _render(node: _Node, part_id: str, message_id: str, store: dict[str, bytes]) -> JsonObject:
    """Render a node tree as Gmail ``MessagePart`` JSON; ``partId`` is the dotted child path."""
    part: JsonObject = {
        "partId": part_id,
        "mimeType": node.mime_type,
        "filename": node.filename,
        "headers": [{"name": name, "value": value} for name, value in node.headers],
    }
    if node.attachment is not None:
        attachment_id = f"att-{message_id}-{len(store) + 1}"
        store[attachment_id] = node.attachment
        part["body"] = {"attachmentId": attachment_id, "size": len(node.attachment)}
    elif node.inline is not None:
        part["body"] = {"size": len(node.inline), "data": b64url_encode(node.inline)}
    else:
        part["body"] = {"size": 0}
    if node.children:
        part["parts"] = [
            _render(child, f"{part_id}.{index}" if part_id else str(index), message_id, store)
            for index, child in enumerate(node.children)
        ]
    return part


def build_messages(builders: Iterable[MessageBuilder]) -> list[FakeMessage]:
    """Build several messages; builders without an id get ``msg-0001``, ``msg-0002``, ..."""
    messages: list[FakeMessage] = []
    for index, builder in enumerate(builders, start=1):
        messages.append(builder.build(builder.message_id or f"msg-{index:04d}"))
    return messages
