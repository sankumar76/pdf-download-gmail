"""Session-wide test configuration.

* Egress guard (AC-8): any non-loopback socket use fails the test (NFR-014 evidence). It is
  installed in ``pytest_configure`` so collection and import-time code are guarded as well.
* The ``req`` and ``perf`` markers are registered in ``pyproject.toml``
  (``--strict-markers`` makes an unregistered marker an error).
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests.support import socket_guard

_restore_sockets: Callable[[], None] | None = None


def pytest_configure(config: pytest.Config) -> None:
    """Block non-loopback sockets for the whole pytest process."""
    global _restore_sockets
    _restore_sockets = socket_guard.install()


def pytest_unconfigure(config: pytest.Config) -> None:
    """Restore the original socket functions."""
    global _restore_sockets
    if _restore_sockets is not None:
        _restore_sockets()
        _restore_sockets = None
