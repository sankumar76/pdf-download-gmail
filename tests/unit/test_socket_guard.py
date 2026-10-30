"""AC-8: the session guard makes a non-loopback connection fail; markers are registered."""

from __future__ import annotations

import socket
import subprocess
import sys
from pathlib import Path

import pytest

from tests.support.socket_guard import NetworkAccessError, is_loopback_host
from tests.support.subprocess_env import guarded_env

pytestmark = pytest.mark.req("NFR-014", "AC-8")

# 203.0.113.0/24 is TEST-NET-3 (RFC 5737): never routable, so a miss could not leak anyway.
DOCUMENTATION_ADDRESS = "203.0.113.7"


def test_create_connection_to_a_remote_address_is_blocked() -> None:
    with pytest.raises(NetworkAccessError):
        socket.create_connection((DOCUMENTATION_ADDRESS, 443), timeout=1)


def test_socket_connect_to_a_remote_address_is_blocked() -> None:
    with socket.socket() as sock, pytest.raises(NetworkAccessError):
        sock.connect((DOCUMENTATION_ADDRESS, 443))


def test_socket_connect_ex_to_a_remote_address_is_blocked() -> None:
    with socket.socket() as sock, pytest.raises(NetworkAccessError):
        sock.connect_ex((DOCUMENTATION_ADDRESS, 443))


def test_remote_host_name_is_blocked_without_a_dns_lookup() -> None:
    with pytest.raises(NetworkAccessError, match="example.com"):
        socket.create_connection(("example.com", 443), timeout=1)


def test_loopback_connection_is_allowed() -> None:
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        with socket.create_connection(("127.0.0.1", port), timeout=5) as client:
            assert client.getpeername()[0] == "127.0.0.1"


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("localhost", True),
        ("LOCALHOST", True),
        ("127.0.0.1", True),
        ("127.5.5.5", True),
        ("::1", True),
        ("::ffff:127.0.0.1", True),
        ("203.0.113.7", False),
        ("::ffff:203.0.113.7", False),
        ("example.com", False),
        ("", False),
        (None, False),
    ],
)
def test_is_loopback_host(host: object, expected: bool) -> None:
    assert is_loopback_host(host) is expected


def test_guard_also_applies_in_a_guarded_subprocess(tmp_path: Path) -> None:
    code = (
        "import socket\n"
        "try:\n"
        f"    socket.create_connection(('{DOCUMENTATION_ADDRESS}', 443), timeout=1)\n"
        "except RuntimeError as exc:\n"
        "    print(type(exc).__name__)\n"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=guarded_env(),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.stdout.strip() == "NetworkAccessError", result.stderr


def test_req_and_perf_markers_are_registered(pytestconfig: pytest.Config) -> None:
    markers = "\n".join(pytestconfig.getini("markers"))

    assert "req(" in markers
    assert "perf:" in markers
