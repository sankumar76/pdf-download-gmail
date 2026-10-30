"""Egress guard for the test suite (AC-8, NFR-014 evidence).

``install()`` replaces ``socket.socket.connect``, ``socket.socket.connect_ex`` and
``socket.create_connection`` with versions that raise ``NetworkAccessError`` unless the
destination is loopback (or a Unix-domain path). Host names other than ``localhost`` are
refused without being resolved, so no DNS query leaves the machine either.

The module has no dependency on ``gmail_pdf`` so that ``sitecustomize.py`` can use it to
guard subprocesses started by tests.
"""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable
from typing import Any


class NetworkAccessError(RuntimeError):
    """Raised when test code tries to reach a non-loopback host."""


def is_loopback_host(host: object) -> bool:
    """Return True for ``localhost`` and loopback IP literals (IPv4, IPv6, mapped)."""
    if not isinstance(host, str):
        return False
    if host.lower() == "localhost":
        return True
    try:
        address = ipaddress.ip_address(host.split("%", 1)[0])
    except ValueError:
        return False
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        return address.ipv4_mapped.is_loopback
    return address.is_loopback


def _check_address(address: object) -> None:
    """Allow Unix-domain paths and loopback ``(host, port, ...)`` tuples; refuse the rest."""
    if isinstance(address, (str, bytes)):  # AF_UNIX path
        return
    host = address[0] if isinstance(address, tuple) and address else address
    if not is_loopback_host(host):
        raise NetworkAccessError(
            f"Blocked non-loopback network access to {host!r}; tests must not use the network"
        )


def install() -> Callable[[], None]:
    """Install the guard and return a function that restores the original socket functions."""
    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex
    original_create_connection = socket.create_connection

    def guarded_connect(self: socket.socket, address: Any) -> None:  # noqa: ANN401
        _check_address(address)
        original_connect(self, address)

    def guarded_connect_ex(self: socket.socket, address: Any) -> int:  # noqa: ANN401
        _check_address(address)
        return original_connect_ex(self, address)

    def guarded_create_connection(address: Any, *args: Any, **kwargs: Any) -> socket.socket:  # noqa: ANN401
        _check_address(address)
        return original_create_connection(address, *args, **kwargs)

    socket.socket.connect = guarded_connect  # type: ignore[method-assign,assignment]
    socket.socket.connect_ex = guarded_connect_ex  # type: ignore[method-assign,assignment]
    socket.create_connection = guarded_create_connection  # type: ignore[assignment]

    def restore() -> None:
        socket.socket.connect = original_connect  # type: ignore[method-assign]
        socket.socket.connect_ex = original_connect_ex  # type: ignore[method-assign]
        socket.create_connection = original_create_connection

    return restore
