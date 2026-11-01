"""Mailbox files for the command-line tests (in-process and subprocess).

The edge mailbox holds the four messages of PGD-15 AC-2, received at Asia/Kolkata wall-clock
times around the range 2026-01-01..2026-01-31: two inside, two outside by exactly one second.
"""

from __future__ import annotations

from pathlib import Path

from tests.fakes.fake_gmail import FakeGmail
from tests.fakes.fake_gmail_json import dump_fake_gmail_to_json_file
from tests.fixtures.builders import MessageBuilder, build_messages

KOLKATA = "Asia/Kolkata"
RANGE_ARGS = ["--start", "2026-01-01", "--end", "2026-01-31", "--tz", KOLKATA]
MESSAGES_IN_RANGE_LINE = "Messages in range: 2\n"


def edge_mailbox() -> FakeGmail:
    """Two messages in the January range and the two seconds just outside it."""
    builders = [
        MessageBuilder("first-second").received("2026-01-01T00:00:00", KOLKATA),
        MessageBuilder("last-second").received("2026-01-31T23:59:59", KOLKATA),
        MessageBuilder("next-midnight").received("2026-02-01T00:00:00", KOLKATA),
        MessageBuilder("second-before").received("2025-12-31T23:59:59", KOLKATA),
    ]
    return FakeGmail(build_messages(builder.pdf("Edge.pdf") for builder in builders))


def write_edge_mailbox(path: Path) -> Path:
    """Write the edge mailbox to ``path`` and return it."""
    dump_fake_gmail_to_json_file(edge_mailbox(), path)
    return path


def empty_mailbox() -> FakeGmail:
    """A mailbox with no message at all: the search for any range returns nothing (PGD-17 AC-1)."""
    return FakeGmail([])


def outside_mailbox() -> FakeGmail:
    """The two edge messages one second outside the January range (PGD-17 AC-2).

    The search is widened by one second on each side, so it returns both; the local re-check
    drops them.
    """
    builders = [
        MessageBuilder("next-midnight").received("2026-02-01T00:00:00", KOLKATA),
        MessageBuilder("second-before").received("2025-12-31T23:59:59", KOLKATA),
    ]
    return FakeGmail(build_messages(builder.pdf("Edge.pdf") for builder in builders))


def write_empty_mailbox(path: Path) -> Path:
    """Write the empty mailbox to ``path`` and return it."""
    dump_fake_gmail_to_json_file(empty_mailbox(), path)
    return path


def write_outside_mailbox(path: Path) -> Path:
    """Write the all-outside mailbox to ``path`` and return it."""
    dump_fake_gmail_to_json_file(outside_mailbox(), path)
    return path
