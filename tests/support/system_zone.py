"""Stand-ins for ``tzlocal.get_localzone_name`` in the time-zone tests (PGD-16 AC-4, PGD-84).

``UNRESOLVED_FORMS`` has one row per way the system zone can be unidentified (D-75): every class
``tzlocal`` can fail with and an empty name. Each class has its own row, so dropping one from the
``except`` in ``infra.tz.system_zone_name`` fails a row.
"""

from __future__ import annotations

from collections.abc import Callable
from zoneinfo import ZoneInfoNotFoundError

import pytest


def raising(error: Exception) -> Callable[[], str]:
    """A ``get_localzone_name`` stand-in that fails with ``error``."""

    def lookup() -> str:
        raise error

    return lookup


def reporting(name: str) -> Callable[[], str]:
    """A ``get_localzone_name`` stand-in that reports ``name``."""
    return lambda: name


NOT_AN_IANA_NAME = "Mars/Olympus"

UNRESOLVED_FORMS = [
    pytest.param(reporting(""), id="empty-name"),
    pytest.param(raising(LookupError("no zone key")), id="lookup-error"),
    pytest.param(raising(ZoneInfoNotFoundError("no zone")), id="zone-info-not-found"),
    pytest.param(raising(ValueError("bad zone")), id="value-error"),
    pytest.param(raising(OSError("no zone")), id="os-error"),
    pytest.param(raising(AttributeError("no encode")), id="attribute-error"),
    pytest.param(raising(TypeError("not a string")), id="type-error"),
]
