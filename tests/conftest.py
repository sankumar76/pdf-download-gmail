"""Session-wide test configuration.

* Egress guard (AC-8): any non-loopback socket connection fails the test (NFR-014 evidence).
* The ``req`` and ``perf`` markers are registered in ``pyproject.toml``
  (``--strict-markers`` makes an unregistered marker an error).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from tests.support import socket_guard


@pytest.fixture(scope="session", autouse=True)
def _block_non_loopback_sockets() -> Iterator[None]:
    """Block non-loopback sockets for the whole pytest session."""
    restore = socket_guard.install()
    try:
        yield
    finally:
        restore()
