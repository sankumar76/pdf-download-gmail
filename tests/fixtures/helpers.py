"""Small helpers shared by the FakeGmail test modules."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import date, timedelta

from gmail_pdf.app.ports import GmailPort
from tests.fakes.fake_gmail import DEFAULT_PAGE_SIZE, FakeGmail
from tests.fixtures.builders import MessageBuilder, build_messages, epoch_ms

BASELINE_QUERY = "has:attachment filename:pdf"


def numbered_mailbox(
    count: int,
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    shuffle_seed: int | None = None,
    latency_s: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
) -> FakeGmail:
    """`count` PDF messages ``m00``... received one hour apart (``m00`` oldest)."""
    builders = [
        MessageBuilder(f"m{index:02d}").received(f"2026-01-15T{index:02d}:00:00").pdf("a.pdf")
        for index in range(count)
    ]
    return FakeGmail(
        build_messages(builders),
        page_size=page_size,
        shuffle_seed=shuffle_seed,
        latency_s=latency_s,
        sleep=sleep,
    )


def list_all(fake: GmailPort, query: str = BASELINE_QUERY) -> list[str]:
    """Follow every page token and return all ids in the order the fake lists them."""
    ids: list[str] = []
    token: str | None = None
    while True:
        page = fake.list_message_ids(query, page_token=token)
        ids.extend(page.message_ids)
        token = page.next_page_token
        if token is None:
            return ids


def day_bounds(day: str, tz: str) -> tuple[int, int]:
    """Epoch seconds of local 00:00 on `day` and on the next day (independent of the fake)."""
    start = date.fromisoformat(day)
    first = epoch_ms(f"{start}T00:00:00", tz) // 1000
    last = epoch_ms(f"{start + timedelta(days=1)}T00:00:00", tz) // 1000
    return first, last
