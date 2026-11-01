"""Test-only mapping from Gmail part resources to ``PartInfo`` (STORY-03.01, AC-6 and AC-7).

The part walker is STORY-03.02, so until it exists a test flattens a built message with
``iter_parts`` and maps each part here. ``RecordingMapping`` wraps a resource and notes every
key read, so a test can prove which fields the mapping, and therefore the rule, looked at.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping

from gmail_pdf.domain.models import PartInfo
from tests.fakes.fake_gmail import iter_parts


def part_info(part: Mapping[str, object]) -> PartInfo:
    """Map one Gmail ``MessagePart`` resource to ``PartInfo``, reading metadata keys only."""
    body = part.get("body")
    size = body.get("size", 0) if isinstance(body, Mapping) else 0
    return PartInfo(
        part_id=str(part.get("partId", "")),
        mime_type=str(part.get("mimeType", "")),
        filename=str(part.get("filename", "")),
        size=size if isinstance(size, int) else 0,
        has_attachment_id=isinstance(body, Mapping) and bool(body.get("attachmentId")),
    )


def part_infos(payload: Mapping[str, object]) -> list[PartInfo]:
    """``PartInfo`` for the payload and every part nested in it, in document order."""
    return [part_info(part) for part in iter_parts(payload)]


class RecordingMapping(Mapping[str, object]):
    """A read-only view of a resource that records the path of every key read.

    A read is a ``[]``, ``get`` or ``in`` on a key, recorded as a tuple of keys from the root
    (``("body", "data")``). Iterating a mapping is recorded as ``(..., "*")``: reading
    everything would hide which field mattered. Nested mappings and lists come back wrapped.
    """

    def __init__(
        self,
        data: Mapping[str, object],
        reads: list[tuple[str, ...]],
        path: tuple[str, ...] = (),
    ) -> None:
        self._data = data
        self._reads = reads
        self._path = path

    def __getitem__(self, key: str) -> object:
        self._reads.append((*self._path, key))
        return self._wrap(self._data[key], key)

    def __iter__(self) -> Iterator[str]:
        self._reads.append((*self._path, "*"))
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def _wrap(self, value: object, key: str) -> object:
        path = (*self._path, key)
        if isinstance(value, Mapping):
            return RecordingMapping(value, self._reads, path)
        if isinstance(value, list):
            return [self._wrap(item, key) for item in value]
        return value
