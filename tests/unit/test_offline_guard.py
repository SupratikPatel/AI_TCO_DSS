"""Offline guard (Req 41.8)."""

import socket

import pytest
from hypothesis import settings


def test_socket_connect_raises() -> None:
    """Req 41.8: a connection attempt to a non-loopback host raises during tests."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with pytest.raises(OSError, match="Network access is disabled"):
            sock.connect(("192.0.2.1", 80))  # TEST-NET-1, never routed
    finally:
        sock.close()


def test_hypothesis_default_profile_loaded() -> None:
    """The default hypothesis profile uses 100 examples and no deadline."""
    assert settings().max_examples == 100
    assert settings().deadline is None
