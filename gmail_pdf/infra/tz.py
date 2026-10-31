"""Time-zone resolution (FR-008, ADR-002 rule 5).

The default zone is the system zone, read with ``tzlocal``; every zone object is a
``zoneinfo.ZoneInfo``. ``tzdata`` is a hard dependency, so the same IANA data is used on every
operating system, Windows included. Wording of the rejections for an unknown zone is
STORY-02.03's; here they only keep the failure out of the "unexpected failure" path.
"""

from __future__ import annotations

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import tzlocal

from gmail_pdf.domain import messages
from gmail_pdf.domain.errors import InputValidationError


def system_zone_name() -> str:
    """The IANA name of the system zone.

    Raises:
        InputValidationError: The system zone cannot be determined (the user can pass ``--tz``).
    """
    try:
        name = tzlocal.get_localzone_name()
    except (ZoneInfoNotFoundError, ValueError, OSError) as exc:
        raise InputValidationError(messages.SYSTEM_ZONE_UNAVAILABLE) from exc
    if not name:
        raise InputValidationError(messages.SYSTEM_ZONE_UNAVAILABLE)
    return name


def resolve_zone(name: str | None) -> ZoneInfo:
    """Return the zone for ``name``, or the system zone when ``name`` is ``None``.

    Raises:
        InputValidationError: ``name`` is not an IANA zone known to ``zoneinfo``/``tzdata``, or
            the system zone cannot be determined. The message never echoes ``name``.
    """
    zone_name = system_zone_name() if name is None else name
    try:
        return ZoneInfo(zone_name)
    except (ZoneInfoNotFoundError, ValueError, OSError) as exc:
        # ValueError: not a normalised relative key; OSError: a key that names a directory.
        raise InputValidationError(messages.ZONE_UNKNOWN) from exc
