"""JSON persistence for ``FakeGmail`` (the file behind ``GMAIL_PDF_TEST_FAKE_MAILBOX``).

Only mailbox content and static settings are stored; scripted faults, recorded calls and
paging cursors are in-process state and are not serialised. Malformed documents raise
``ValueError``.

Everything the fake later reads from a document is checked here, at load (PGD-15 AC-6 iii,
QUA-39): for any file content the command line ends in success or in the one fixed
"mailbox file could not be read" line, never in a bare exception from a later listing or
read. A depth cap over the whole document, unread keys included, keeps ``copy.deepcopy`` and
the recursive part walk well inside the interpreter's recursion limit. Not covered: a
``MemoryError`` on a huge file, and reads that later stories add (they keep the rule).
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


# Containers (objects and arrays) from the document root down; the root is level 1. Real Gmail
# resources nest parts a handful of levels deep, so 200 is far above any honest file and below
# the depth at which ``copy.deepcopy`` and the recursive part walk run out of stack.
MAX_DOCUMENT_DEPTH = 200
# Epoch milliseconds are 13 digits until the year 2286; 20 leaves room and stays far below
# the interpreter's integer-string limit (4300 digits).
MAX_INTERNAL_DATE_DIGITS = 20
# One hour per call; ``time.sleep`` overflows long before a float parser stops accepting.
MAX_LATENCY_S = 3600.0


def _require_shallow(document: object) -> None:
    """Fail when any object or array sits deeper than ``MAX_DOCUMENT_DEPTH`` (iterative walk)."""
    pending: list[tuple[object, int]] = [(document, 1)]
    while pending:
        node, level = pending.pop()
        if isinstance(node, dict):
            children: list[object] = list(node.values())
        elif isinstance(node, list):
            children = list(node)
        else:
            continue
        if level > MAX_DOCUMENT_DEPTH:
            raise ValueError(f"fake mailbox JSON is nested deeper than {MAX_DOCUMENT_DEPTH} levels")
        pending.extend((child, level + 1) for child in children)


def _require_part_tree(root: Mapping[str, object]) -> None:
    """Every ``parts`` entry, at any depth, is a list of objects (explicit stack, no recursion)."""
    pending: list[Mapping[str, object]] = [root]
    while pending:
        part = pending.pop()
        children = part.get("parts")
        if children is None:
            continue
        if not isinstance(children, list) or not all(isinstance(c, dict) for c in children):
            raise ValueError("each fake mailbox 'parts' must be a list of objects")
        pending.extend(children)


def _require_listable(resource: Mapping[str, object]) -> None:
    """Fail at load time when a resource would make a later listing or read raise.

    ``FakeGmail`` reads ``payload`` (part tree, headers), ``labelIds`` (spam and trash),
    ``internalDate`` (ordering, ``after:`` and ``before:``) of every message it lists; Gmail
    returns ``internalDate`` as a decimal string.
    """
    payload = resource.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("each fake mailbox message resource needs an object 'payload'")
    date = resource.get("internalDate")
    if not (
        isinstance(date, str)
        and date.isascii()
        and date.isdecimal()
        and len(date) <= MAX_INTERNAL_DATE_DIGITS
    ):
        raise ValueError("each fake mailbox message resource needs a decimal string 'internalDate'")
    if "labelIds" in resource:
        labels = resource["labelIds"]
        if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
            raise ValueError("fake mailbox 'labelIds' must be a list of strings")
    headers = payload.get("headers", [])
    if not isinstance(headers, list) or not all(isinstance(h, dict) for h in headers):
        raise ValueError("fake mailbox 'headers' must be a list of objects")
    _require_part_tree(payload)


def _latency_s(value: object) -> float:
    """Parse ``latency_s``; within ``[0, MAX_LATENCY_S]`` so a sleep cannot raise.

    The range test also refuses ``inf`` and ``nan``, which no comparison with a number accepts.
    """
    latency = float(str(value))
    if not 0.0 <= latency <= MAX_LATENCY_S:
        raise ValueError("fake mailbox 'latency_s' must be a finite number of seconds")
    return latency


def from_json_dict(data: Mapping[str, object]) -> FakeGmail:
    """Rebuild a fake from ``to_json_dict`` output.

    Raises:
        ValueError: the document is malformed, too deeply nested, or holds a value the fake
            could not read later (a ``RecursionError`` is never raised from here).
    """
    _require_shallow(data)
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
        _require_listable(resource)
        decoded = {str(k): b64url_decode(str(v)) for k, v in attachments.items()}
        messages.append(FakeMessage(resource, decoded))
    seed = data.get("shuffle_seed")
    return FakeGmail(
        messages,
        page_size=int(str(data.get("page_size", DEFAULT_PAGE_SIZE))),
        shuffle_seed=None if seed is None else int(str(seed)),
        latency_s=_latency_s(data.get("latency_s", 0.0)),
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
