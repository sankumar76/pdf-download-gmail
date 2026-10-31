"""Time-zone resolution and the real clock (FR-008, ADR-002 rule 5).

The default zone is the system zone, read with ``tzlocal``; every zone object is a
``zoneinfo.ZoneInfo``. ``tzdata`` is a hard dependency, so the same IANA data is used on every
operating system, Windows included. Whether a name is acceptable to the user is decided by
``domain.validation`` before anything here runs; this module only looks names up.
"""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from zoneinfo import ZoneInfo

import tzlocal


def system_zone_name() -> str | None:
    """The IANA name of the system zone, or ``None`` when it cannot be determined.

    ``tzlocal`` has no single failure type. ``LookupError`` covers a registry without a zone
    key (and ``ZoneInfoNotFoundError``, which is a ``KeyError``); ``ValueError`` and ``OSError``
    cover an unreadable or malformed source; ``AttributeError`` and ``TypeError`` cover a registry
    value of the wrong type (PGD-16 AC-4). A listed class includes its subclasses.
    """
    try:
        name = tzlocal.get_localzone_name()
    except (LookupError, ValueError, OSError, AttributeError, TypeError):
        return None
    return name or None


def resolve_zone(name: str | None) -> ZoneInfo:
    """Return the zone for ``name``, or the system zone when ``name`` is ``None``.

    Raises:
        ValueError: the system zone is wanted but cannot be determined.
        ZoneInfoNotFoundError: ``name`` is not a zone ``zoneinfo`` knows. Both are programming
            errors: a validated request names a known zone (``domain.validation``).
    """
    zone_name = system_zone_name() if name is None else name
    if zone_name is None:
        raise ValueError("the system time zone cannot be determined")
    return ZoneInfo(zone_name)


class SystemClock:
    """The real clock: today's date in a given zone (the ``Clock`` port, ``app.ports``)."""

    def today(self, zone: tzinfo) -> date:
        """The current calendar date in ``zone``."""
        return datetime.now(zone).date()
