"""Shared pytest configuration: offline guard and hypothesis profile (Req 41.8)."""

import socket
from collections.abc import Callable, Iterator

import pytest
from hypothesis import settings

settings.register_profile("default", max_examples=100, deadline=None, derandomize=False)
settings.load_profile("default")

# Loopback connections stay on the machine. Windows asyncio needs them to build its
# internal socket pair (socket.socketpair falls back to a loopback TCP connection).
LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


def _offline_connect(original: Callable[..., None]) -> Callable[..., None]:
    def connect(sock: socket.socket, address: object) -> None:
        host = address[0] if isinstance(address, tuple) else address
        if host not in LOOPBACK_HOSTS:
            raise OSError(f"Network access is disabled during tests (Req 41.8): {address!r}")
        original(sock, address)

    return connect


@pytest.fixture(autouse=True, scope="session")
def offline_guard() -> Iterator[None]:
    """Make every non-loopback socket connection raise for the whole test session."""
    patcher = pytest.MonkeyPatch()
    patcher.setattr(socket.socket, "connect", _offline_connect(socket.socket.connect))
    yield
    patcher.undo()
