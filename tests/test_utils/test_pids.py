from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.utils.pids import get_pid_by_local_and_remote_port


class PidsTests(unittest.TestCase):
    def test_get_pid_by_local_and_remote_port_skips_connections_without_endpoints(
        self,
    ) -> None:
        connections = [
            SimpleNamespace(laddr=(), raddr=(), pid=1),
            SimpleNamespace(
                laddr=SimpleNamespace(port=5555),
                raddr=SimpleNamespace(port=6666),
                pid=42,
            ),
        ]

        with patch("src.utils.pids.psutil.net_connections", return_value=connections):
            self.assertEqual(get_pid_by_local_and_remote_port(5555, 6666), 42)

    def test_get_pid_by_local_and_remote_port_returns_none_when_missing(self) -> None:
        connections = [
            SimpleNamespace(
                laddr=SimpleNamespace(port=5555),
                raddr=SimpleNamespace(port=7777),
                pid=42,
            )
        ]

        with patch("src.utils.pids.psutil.net_connections", return_value=connections):
            self.assertIsNone(get_pid_by_local_and_remote_port(5555, 6666))
