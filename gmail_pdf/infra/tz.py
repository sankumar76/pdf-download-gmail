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

from gmail_pdf.domain.validation import FALLBACK_ZONE_NAME, is_known_zone


def system_zone_name() -> str | None:
    """The IANA name of the system zone, or ``None`` when it cannot be determined.

    ``tzlocal`` has no single failure type. ``LookupError`` covers a registry without a zone
    key (and ``ZoneInfoNotFoundError``, which is a ``KeyError``); ``ValueError`` and ``OSError``
    cover an unreadable or malformed source; ``AttributeError`` and ``TypeError`` cover a registry
    value of the wrong type (PGD-16 AC-4). A listed class includes its subclasses.

    Without time-zone data for ``FALLBACK_ZONE_NAME`` the answer is also ``None``, whatever
    ``tzlocal`` names (PGD-84 AC-8): on Windows ``tzlocal`` needs no ``tzdata``, so a broken
    install still reports a real name, and the run must stop at the fallback (exit 1) rather than
    continue in a zone no data backs. A name that ``zoneinfo`` does not know on a healthy install
    is returned as it is, so the request is rejected (AC-7).
    """
    try:
        name = tzlocal.get_localzone_name()
    except (LookupError, ValueError, OSError, AttributeError, TypeError):
        return None
    if not name or not is_known_zone(FALLBACK_ZONE_NAME):
        return None
    return name


def resolve_zone(name: str | None) -> ZoneInfo:
    """Return the zone for ``name``; for ``None``, the system zone, else ``FALLBACK_ZONE_NAME``.

    Raises:
        ZoneInfoNotFoundError: ``name`` is not a zone ``zoneinfo`` knows. A programming error: a
            validated request names a known zone (``domain.validation``).
    """
    zone_name = (system_zone_name() or FALLBACK_ZONE_NAME) if name is None else name
    return ZoneInfo(zone_name)


class SystemClock:
    """The real clock: today's date in a given zone (the ``Clock`` port, ``app.ports``)."""

    def today(self, zone: tzinfo) -> date:
        """The current calendar date in ``zone``."""
        return datetime.now(zone).date()
