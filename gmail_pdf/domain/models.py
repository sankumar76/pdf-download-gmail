"""Records shared by the application and its front ends (architecture 4.1).

Only what the date-range slice needs exists so far; the other records of the model (message
plans, PDF candidates, outcomes) arrive with the stories that use them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum, IntEnum


class ExitCode(IntEnum):
    """Process exit codes: a closed set 0 to 3 (architecture 6.5, decision D-21)."""

    OK = 0
    FAILURE = 1  # the run did not complete cleanly: unexpected failure, cancel, test-hook failure
    USAGE = 2  # bad arguments
    AUTH_FAILED = 3  # credentials or sign-in


class RunResult(Enum):
    """How a run ended. Only the outcomes this slice can reach exist so far."""

    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class RunRequest:
    """A range that passed ``domain.validation``; only ``validate`` builds one.

    Attributes:
        start: First day of the range, inclusive.
        end: Last day of the range, inclusive.
        tz: IANA zone name, or ``None`` for the system zone (FR-008).
    """

    start: date
    end: date
    tz: str | None = None


@dataclass(frozen=True, slots=True)
class MessageRef:
    """A message that passed the local range check (NFR-009: ids and date only).

    Attributes:
        message_id: The Gmail message id.
        internal_date_ms: Gmail ``internalDate``, epoch milliseconds.
    """

    message_id: str
    internal_date_ms: int


@dataclass(frozen=True, slots=True)
class RunSummary:
    """The outcome of a run.

    Attributes:
        result: How the run ended.
        messages: The messages in the range, in the order they were found (ordering is
            STORY-02.05).
    """

    result: RunResult
    messages: tuple[MessageRef, ...] = ()

    @property
    def exit_code(self) -> ExitCode:
        """The process exit code for this outcome."""
        return ExitCode.OK if self.result is RunResult.COMPLETED else ExitCode.FAILURE
