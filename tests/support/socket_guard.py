"""Egress guard for the test suite (AC-8, NFR-014 evidence).

``install()`` replaces the socket entry points that can reach a remote host:
``socket.socket.connect``, ``connect_ex`` and ``sendto`` (UDP), plus
``socket.create_connection``, ``getaddrinfo`` and ``gethostbyname``. Each raises
``NetworkAccessError`` unless the destination is loopback (or a Unix-domain path). Host names
other than ``localhost`` are refused *before* resolution, so no DNS query leaves the machine.

Not covered, by design: raw sockets, ``socket.socket.send`` on an already-connected socket
(it can only be connected through a guarded call) and non-socket I/O.

The module has no dependency on ``gmail_pdf`` so that ``sitecustomize.py`` can use it to
guard subprocesses started by tests. ``tests/conftest.py`` installs it in ``pytest_configure``,
so code that runs at collection or import time is guarded too.
"""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable
from typing import Any

# 203.0.113.0/24 is TEST-NET-3 (RFC 5737): never routable, so tests may use it as a "remote" host.
DOCUMENTATION_ADDRESS = "203.0.113.7"


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


def _check_host(host: object) -> None:
    """Allow ``None``/empty (the local machine) and loopback hosts; refuse everything else."""
    if host in (None, "", b"") or is_loopback_host(host):
        return
    raise NetworkAccessError(
        f"Blocked non-loopback network access to {host!r}; tests must not use the network"
    )


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
    original_sendto = socket.socket.sendto
    original_create_connection = socket.create_connection
    original_getaddrinfo = socket.getaddrinfo
    original_gethostbyname = socket.gethostbyname

    # The wrappers must accept whatever the stdlib accepts, so their parameters are `Any`
    # (the same reason typeshed uses its `_Address` alias for socket addresses).
    def guarded_connect(self: socket.socket, address: Any) -> None:
        _check_address(address)
        original_connect(self, address)

    def guarded_connect_ex(self: socket.socket, address: Any) -> int:
        _check_address(address)
        return original_connect_ex(self, address)

    def guarded_sendto(self: socket.socket, data: Any, *args: Any) -> int:
        _check_address(args[-1])  # sendto(data, address) or sendto(data, flags, address)
        return original_sendto(self, data, *args)

    def guarded_create_connection(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        _check_address(address)
        return original_create_connection(address, *args, **kwargs)

    def guarded_getaddrinfo(host: Any, *args: Any, **kwargs: Any) -> Any:
        _check_host(host)
        return original_getaddrinfo(host, *args, **kwargs)

    def guarded_gethostbyname(host: Any) -> str:
        _check_host(host)
        return original_gethostbyname(host)

    # Monkeypatching stdlib callables: mypy rejects assigning to a method or a function
    # (`method-assign` / `assignment`), which is exactly what a guard has to do.
    socket.socket.connect = guarded_connect  # type: ignore[method-assign,assignment]
    socket.socket.connect_ex = guarded_connect_ex  # type: ignore[method-assign,assignment]
    socket.socket.sendto = guarded_sendto  # type: ignore[method-assign,assignment]
    socket.create_connection = guarded_create_connection  # type: ignore[assignment]
    socket.getaddrinfo = guarded_getaddrinfo  # type: ignore[assignment]
    socket.gethostbyname = guarded_gethostbyname  # type: ignore[assignment]

    def restore() -> None:
        socket.socket.connect = original_connect  # type: ignore[method-assign]
        socket.socket.connect_ex = original_connect_ex  # type: ignore[method-assign]
        socket.socket.sendto = original_sendto  # type: ignore[method-assign]
        socket.create_connection = original_create_connection
        socket.getaddrinfo = original_getaddrinfo
        socket.gethostbyname = original_gethostbyname

    return restore
