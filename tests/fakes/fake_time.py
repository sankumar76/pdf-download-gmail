"""Time doubles for the retry helper (test-strategy section 3): no real sleeping, no real clock.

* ``FakeClock``: a settable "now" that the retry helper reads for HTTP-date ``Retry-After``.
* ``FakeSleeper``: records every requested sleep and moves the fake clock forward by it.
* ``FakeCancelToken``: a ``CancelToken`` whose ``wait`` goes through the sleeper, so a backoff
  of 64 s takes no time, while ``set`` / ``is_set`` behave exactly as the real token does.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from gmail_pdf.domain.events import CancelToken

DEFAULT_START = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


class FakeClock:
    """A clock that only moves when told to."""

    def __init__(self, start: datetime = DEFAULT_START) -> None:
        self._now = start

    def now(self) -> datetime:
        """The current fake time (timezone-aware, UTC)."""
        return self._now

    def advance(self, seconds: float) -> None:
        """Move the clock forward."""
        self._now += timedelta(seconds=seconds)


class FakeSleeper:
    """Records sleeps instead of performing them."""

    def __init__(self, clock: FakeClock | None = None) -> None:
        self.clock = clock if clock is not None else FakeClock()
        self.delays: list[float] = []

    def sleep(self, seconds: float) -> None:
        """Record ``seconds`` and advance the fake clock by it."""
        self.delays.append(seconds)
        self.clock.advance(seconds)


class FakeCancelToken(CancelToken):
    """A ``CancelToken`` that sleeps through a ``FakeSleeper``.

    Args:
        sleeper: Receives every ``wait`` as a sleep.
        cancel_during_sleep: If given, the token is set during that sleep (1 = the first one),
            as if the user pressed Cancel while the program was waiting.
    """

    def __init__(self, sleeper: FakeSleeper, cancel_during_sleep: int | None = None) -> None:
        super().__init__()
        self._sleeper = sleeper
        self._cancel_during_sleep = cancel_during_sleep

    def wait(self, timeout: float | None = None) -> bool:
        if self.is_set():
            return True
        self._sleeper.sleep(0.0 if timeout is None else timeout)
        if self._cancel_during_sleep == len(self._sleeper.delays):
            self.set()
        return self.is_set()
