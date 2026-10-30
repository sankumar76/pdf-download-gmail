"""JSON persistence for ``FakeGmail`` (the file behind ``GMAIL_PDF_TEST_FAKE_MAILBOX``).

Only mailbox content and static settings are stored; scripted faults, recorded calls and
paging cursors are in-process state and are not serialised. Malformed documents raise
``ValueError``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from gmail_pdf.app.ports import JsonObject
from tests.fakes.fake_gmail import (
    DEFAULT_EPOCH_BOUNDS,
    DEFAULT_PAGE_SIZE,
    EpochBounds,
    FakeGmail,
    FakeMessage,
    b64url_decode,
    b64url_encode,
)

JSON_FORMAT_VERSION = 1


def to_json_dict(fake: FakeGmail) -> JsonObject:
    """Serialise mailbox content and static settings."""
    return {
        "format": JSON_FORMAT_VERSION,
        "page_size": fake.page_size,
        "shuffle_seed": fake.shuffle_seed,
        "latency_s": fake.latency_s,
        "epoch_bounds": fake.epoch_bounds.value,
        "messages": [
            {
                "resource": message.resource,
                "attachments": {k: b64url_encode(v) for k, v in message.attachments.items()},
            }
            for message in fake.messages
        ],
    }


def from_json_dict(data: Mapping[str, object]) -> FakeGmail:
    """Rebuild a fake from ``to_json_dict`` output."""
    if data.get("format") != JSON_FORMAT_VERSION:
        raise ValueError(f"unsupported fake mailbox format {data.get('format')!r}")
    raw_messages = data.get("messages")
    if not isinstance(raw_messages, list):
        raise ValueError("fake mailbox 'messages' must be a list")
    messages: list[FakeMessage] = []
    for entry in raw_messages:
        resource = entry.get("resource") if isinstance(entry, dict) else None
        attachments = entry.get("attachments") if isinstance(entry, dict) else None
        if not isinstance(resource, dict) or not isinstance(attachments, dict):
            raise ValueError("each fake mailbox message needs 'resource' and 'attachments'")
        if not isinstance(resource.get("id"), str) or not resource["id"]:
            raise ValueError("each fake mailbox message resource needs a string 'id'")
        decoded = {str(k): b64url_decode(str(v)) for k, v in attachments.items()}
        messages.append(FakeMessage(resource, decoded))
    seed = data.get("shuffle_seed")
    return FakeGmail(
        messages,
        page_size=int(str(data.get("page_size", DEFAULT_PAGE_SIZE))),
        shuffle_seed=None if seed is None else int(str(seed)),
        latency_s=float(str(data.get("latency_s", 0.0))),
        epoch_bounds=EpochBounds(str(data.get("epoch_bounds", DEFAULT_EPOCH_BOUNDS.value))),
    )


def dump_fake_gmail_to_json_file(fake: FakeGmail, path: Path) -> None:
    """Write ``fake`` to ``path`` as UTF-8 JSON."""
    path.write_text(json.dumps(to_json_dict(fake), indent=2), encoding="utf-8")


def load_fake_gmail_from_json_file(path: Path) -> FakeGmail:
    """Load a fake mailbox from JSON (used by the ``GMAIL_PDF_TEST_FAKE_MAILBOX`` hook)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("fake mailbox JSON must be an object")
    return from_json_dict(data)
