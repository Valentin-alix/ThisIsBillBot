from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

# pre-seed: loads src.core.bot.bot before proxy_listener.py triggers __init__.py,
# which would cause a circular import (bot_manager → proxy_listener → bot → __init__ → bot_manager).
import src.core.bot.bot_manager as _bot_manager_seed  # noqa: F401

from src.core.mitm.proxy_listener import ProxyListener


def _make_bot(login: str, account_id: int) -> SimpleNamespace:
    return SimpleNamespace(
        account={"apikey": {"login": login, "accountId": account_id}},
        process_manager=SimpleNamespace(pid=None),
    )


def _make_proxy(bots: dict[int, SimpleNamespace]) -> ProxyListener:
    return ProxyListener(account_by_id=bots)  # type: ignore[arg-type]


class ProxyListenerBotRegistrationTests(TestCase):
    # ── on_connection_port_assigned ──────────────────────────────────────────

    def test_registers_bot_by_login(self) -> None:
        bot = _make_bot("alice", 1)
        proxy = _make_proxy({1: bot})

        proxy.on_connection_port_assigned("alice", 54321)

        self.assertIs(proxy._account_by_connection_port[54321], bot)

    def test_ignores_unknown_login(self) -> None:
        bot = _make_bot("alice", 1)
        proxy = _make_proxy({1: bot})

        proxy.on_connection_port_assigned("unknown", 54321)

        self.assertNotIn(54321, proxy._account_by_connection_port)

    def test_handles_multiple_bots_independently(self) -> None:
        alice = _make_bot("alice", 1)
        bob = _make_bot("bob", 2)
        proxy = _make_proxy({1: alice, 2: bob})

        proxy.on_connection_port_assigned("alice", 11111)
        proxy.on_connection_port_assigned("bob", 22222)

        self.assertIs(proxy._account_by_connection_port[11111], alice)
        self.assertIs(proxy._account_by_connection_port[22222], bob)

    # ── create_bridge ────────────────────────────────────────────────────────

    def _make_sockets(self, server_ip: str) -> tuple[MagicMock, MagicMock]:
        server_socket = MagicMock()
        server_socket.getpeername.return_value = (server_ip, 5555)
        client_socket = MagicMock()
        client_socket.getpeername.return_value = ("10.0.0.1", 12345)
        return client_socket, server_socket

    def test_create_bridge_returns_none_when_port_not_registered(self) -> None:
        proxy = _make_proxy({})

        with patch("src.core.mitm.proxy_listener.CONNECTION_SERVERS_IPS", ["1.2.3.4"]):
            client_socket, server_socket = self._make_sockets("1.2.3.4")
            result = proxy.create_bridge(client_socket, server_socket, 54321)

        self.assertIsNone(result)

    def test_create_bridge_finds_registered_bot_by_connection_port(self) -> None:
        bot = _make_bot("alice", 1)
        proxy = _make_proxy({1: bot})
        proxy._account_by_connection_port[54321] = bot  # type: ignore[assignment]

        with (
            patch("src.core.mitm.proxy_listener.CONNECTION_SERVERS_IPS", ["1.2.3.4"]),
            patch("src.core.mitm.proxy_listener.ConnectionProxy") as MockConnectionProxy,
        ):
            client_socket, server_socket = self._make_sockets("1.2.3.4")
            result = proxy.create_bridge(client_socket, server_socket, 54321)

        self.assertIsNotNone(result)
        _, kwargs = MockConnectionProxy.call_args
        self.assertIs(kwargs["bot"], bot)
