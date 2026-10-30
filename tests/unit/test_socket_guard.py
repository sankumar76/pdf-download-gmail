"""AC-8: the session guard makes non-loopback network use fail; markers are registered."""

from __future__ import annotations

import socket

import pytest

from tests.support.socket_guard import DOCUMENTATION_ADDRESS, NetworkAccessError, is_loopback_host

pytestmark = pytest.mark.req("NFR-014", "AC-8")


def test_create_connection_to_a_remote_address_is_blocked() -> None:
    with pytest.raises(NetworkAccessError):
        socket.create_connection((DOCUMENTATION_ADDRESS, 443), timeout=1)


def test_socket_connect_to_a_remote_address_is_blocked() -> None:
    with socket.socket() as sock, pytest.raises(NetworkAccessError):
        sock.connect((DOCUMENTATION_ADDRESS, 443))


def test_socket_connect_ex_to_a_remote_address_is_blocked() -> None:
    with socket.socket() as sock, pytest.raises(NetworkAccessError):
        sock.connect_ex((DOCUMENTATION_ADDRESS, 443))


def test_udp_sendto_with_data_and_address_is_blocked() -> None:
    with (
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock,
        pytest.raises(NetworkAccessError),
    ):
        sock.sendto(b"x", (DOCUMENTATION_ADDRESS, 53))


def test_udp_sendto_with_data_flags_and_address_is_blocked() -> None:
    with (
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock,
        pytest.raises(NetworkAccessError),
    ):
        sock.sendto(b"x", 0, (DOCUMENTATION_ADDRESS, 53))


def test_remote_host_name_is_blocked_without_a_dns_lookup() -> None:
    with pytest.raises(NetworkAccessError, match="example.com"):
        socket.create_connection(("example.com", 443), timeout=1)


def test_getaddrinfo_for_a_remote_host_is_blocked() -> None:
    with pytest.raises(NetworkAccessError, match="example.com"):
        socket.getaddrinfo("example.com", 443)


def test_gethostbyname_for_a_remote_host_is_blocked() -> None:
    with pytest.raises(NetworkAccessError, match="example.com"):
        socket.gethostbyname("example.com")


def test_gethostbyname_ex_for_a_remote_host_is_blocked() -> None:
    with pytest.raises(NetworkAccessError, match="example.com"):
        socket.gethostbyname_ex("example.com")


def test_gethostbyaddr_for_a_remote_address_is_blocked() -> None:
    with pytest.raises(NetworkAccessError, match=DOCUMENTATION_ADDRESS):
        socket.gethostbyaddr(DOCUMENTATION_ADDRESS)


def test_getnameinfo_for_a_remote_address_is_blocked() -> None:
    with pytest.raises(NetworkAccessError, match=DOCUMENTATION_ADDRESS):
        socket.getnameinfo((DOCUMENTATION_ADDRESS, 80), 0)


def test_getnameinfo_for_loopback_is_allowed() -> None:
    assert socket.getnameinfo(("127.0.0.1", 80), socket.NI_NUMERICHOST | socket.NI_NUMERICSERV)


def test_getaddrinfo_for_loopback_is_allowed() -> None:
    assert socket.getaddrinfo("127.0.0.1", 80)


def test_getaddrinfo_without_a_host_is_allowed() -> None:
    assert socket.getaddrinfo(None, 80)


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
        (DOCUMENTATION_ADDRESS, False),
        (f"::ffff:{DOCUMENTATION_ADDRESS}", False),
        ("example.com", False),
        ("", False),
        (None, False),
    ],
)
def test_is_loopback_host(host: object, expected: bool) -> None:
    assert is_loopback_host(host) is expected


def test_req_and_perf_markers_are_registered(pytestconfig: pytest.Config) -> None:
    markers = "\n".join(pytestconfig.getini("markers"))

    assert "req(" in markers
    assert "perf:" in markers
