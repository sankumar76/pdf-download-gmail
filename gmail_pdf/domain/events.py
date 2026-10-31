"""Progress and notice events (architecture 6.8).

Only the ``Warning`` event and its code enum exist so far; the other events are added by the
stories that emit them. Every event is a frozen dataclass of plain, already-redacted values.
``CancelToken`` (architecture 6.9) is the cancel flag a run checks before every Gmail call and
waits on during a backoff.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from enum import Enum, auto


class WarningCode(Enum):
    """Closed set of notice codes shown to the user as ``warning:`` lines or banners."""

    TOKEN_OUTSIDE_PROFILE = auto()


@dataclass(frozen=True, slots=True)
class Warning:
    """A non-blocking notice for the user (architecture 6.8; the name is the spec's).

    The name shadows the built-in ``Warning`` exception class. Always import this module and
    write ``events.Warning``; never ``from gmail_pdf.domain.events import Warning``.

    Attributes:
        code: Which notice this is.
        count: How many items the notice is about (0 when not applicable).
        text: User-facing wording; empty until the message table (``domain/messages.py``)
            supplies it, so producers never hard-code sentences.
    """

    code: WarningCode
    count: int = 0
    text: str = ""


class CancelToken:
    """A cancel flag shared by the code that starts a run and the code that executes it.

    Wraps one ``threading.Event``. ``wait`` is how a backoff sleeps, so setting the token
    interrupts the sleep at once (NFR-004). Wiring Ctrl+C to ``set`` is STORY-06.02; a signal
    handler must not call ``set`` directly (issue #29).
    """

    def __init__(self) -> None:
        self._event = threading.Event()

    def set(self) -> None:
        """Request cancellation. Safe to call from any thread, and more than once."""
        self._event.set()

    def is_set(self) -> bool:
        """Whether cancellation has been requested."""
        return self._event.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        """Sleep up to ``timeout`` seconds, or until the token is set.

        Returns:
            ``True`` if the token is set (the caller must stop), ``False`` if the time elapsed.
        """
        return self._event.wait(timeout)
