"""Progress and notice events (architecture 6.8).

Only the ``Warning`` event and its code enum exist so far; the other events are added by the
stories that emit them. Every event is a frozen dataclass of plain, already-redacted values.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class WarningCode(Enum):
    """Closed set of notice codes shown to the user as ``warning:`` lines or banners."""

    TOKEN_OUTSIDE_PROFILE = auto()


@dataclass(frozen=True, slots=True)
class Warning:
    """A non-blocking notice for the user (architecture 6.8; the name is the spec's).

    Attributes:
        code: Which notice this is.
        count: How many items the notice is about (0 when not applicable).
        text: User-facing wording; empty until the message table (``domain/messages.py``)
            supplies it, so producers never hard-code sentences.
    """

    code: WarningCode
    count: int = 0
    text: str = ""
