"""Ports: the interfaces the application layer needs from the outside world.

``GmailPort`` is the Gmail seam; ``EventSink`` and the zone resolver are the two other seams the
run needs so far. The remaining ports (token provider, file store, manifest, audit) are added
by the stories that need them. ``Deps`` bundles the implementations ``bootstrap.build_deps``
wires; it lives here so ``app`` can name it without importing ``bootstrap``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from gmail_pdf.domain import events

# A Gmail API resource exactly as the API returns it (JSON object). The shape is owned by
# Google and parsed by ``domain.mime`` later, so it is deliberately untyped at this seam.
JsonObject = dict[str, Any]


@dataclass(frozen=True, slots=True)
class MessageIdPage:
    """One page of ``users.messages.list`` results.

    Attributes:
        message_ids: Message ids on this page, in the order Gmail returned them.
        next_page_token: Token for the next page, or ``None`` on the last page.
    """

    message_ids: tuple[str, ...]
    next_page_token: str | None = None


class GmailPort(Protocol):
    """Read-only Gmail access: exactly the three calls on the NFR-011 allow-list.

    Implementations: ``infra.gmail_gateway`` (real, later story) and ``FakeGmail`` (tests).
    """

    def list_message_ids(
        self,
        query: str,
        *,
        page_token: str | None = None,
        include_spam_trash: bool = False,
    ) -> MessageIdPage:
        """List one page of message ids matching a Gmail search ``query``."""

    def get_message(self, message_id: str) -> JsonObject:
        """Return the message resource with ``format=full`` (nested part tree included)."""

    def get_attachment(self, message_id: str, attachment_id: str) -> bytes:
        """Return the decoded bytes of an attachment body."""


class EventSink(Protocol):
    """Receives the notices a run produces (architecture 6.8); never blocks.

    Only ``Warning`` exists so far. The CLI prints it, the GUI will enqueue it.
    """

    def emit(self, event: events.Warning) -> None:
        """Handle one event."""


# Resolves an IANA zone name (``None`` = the system zone) to a zone, or raises
# ``InputValidationError``. The implementation is ``infra.tz.resolve_zone``.
ZoneResolver = Callable[[str | None], ZoneInfo]


@dataclass(frozen=True, slots=True)
class Deps:
    """Port implementations handed to the application layer (tests substitute fakes)."""

    gmail: GmailPort
    resolve_zone: ZoneResolver
