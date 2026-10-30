"""Session-wide test configuration.

* Egress guard (AC-8): any non-loopback socket use fails the test (NFR-014 evidence). It is
  installed in ``pytest_configure`` so collection and import-time code are guarded as well.
* The ``req`` and ``perf`` markers are registered in ``pyproject.toml``
  (``--strict-markers`` makes an unregistered marker an error).
* Process-wide redaction state (hooks, logger caps, secret registry) is restored after every
  test, because ``cli.main.main`` installs it as its first action (PGD-13 AC-7).
"""

from __future__ import annotations

import logging
import sys
import threading
from collections.abc import Callable, Iterator

import pytest

from gmail_pdf import redaction
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


@pytest.fixture(autouse=True)
def _isolate_process_wide_redaction_state() -> Iterator[None]:
    """Undo what ``cli.main.main`` and the redaction installers change process-wide.

    ``main`` installs the excepthooks and the logging caps on every call, and tests call it
    in-process; without this the hooks, the filter on ``logging.lastResort``, the logger
    levels and the registered secrets would leak from one test into the next.
    """
    names = redaction.THIRD_PARTY_LOGGERS
    levels = {name: logging.getLogger(name).level for name in names}
    last_resort_filters = list(logging.lastResort.filters) if logging.lastResort else []
    hooks = (sys.excepthook, threading.excepthook)
    yield
    sys.excepthook, threading.excepthook = hooks
    if logging.lastResort is not None:
        logging.lastResort.filters[:] = last_resort_filters
    for name, level in levels.items():
        logging.getLogger(name).setLevel(level)
    redaction.clear_secrets()
