import threading
import unittest
from threading import RLock
from unittest.mock import create_autospec

from datas.protos.non_obf.game.basic_pb2 import DateRequest
from datas.protos.non_obf.game.connection_pb2 import PingRequest
from google.protobuf.message import Message

from src.core.behaviors.socket.heartbeat_behavior import HearthBeatBehavior
from src.core.events_manager.event_manager import EventManager
from src.core.states.game_state import GameState
from src.services.logging.logger import Logger

_SHORT_INTERVAL = 0.05


class HearthBeatBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sent_messages: list[Message] = []
        self.event_manager = create_autospec(EventManager, instance=True)
        self.game_state = create_autospec(GameState, instance=True)
        self.logger = create_autospec(Logger, instance=True)
        self.event_manager.lock = RLock()

        def send(msg: Message) -> None:
            self.sent_messages.append(msg)

        def clear_listener_by_origin(_originator: object) -> None:
            return None

        def clear_modifier_by_origin(_originator: object) -> None:
            return None

        self.event_manager.send.side_effect = send
        self.event_manager.clear_listener_by_origin.side_effect = (
            clear_listener_by_origin
        )
        self.event_manager.clear_modifier_by_origin.side_effect = (
            clear_modifier_by_origin
        )

        self.behavior = HearthBeatBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.logger,
        )

    def _patch_interval(self) -> None:
        import src.core.behaviors.socket.heartbeat_behavior as hb_module

        hb_module._HEARTBEAT_INTERVAL_SECONDS = _SHORT_INTERVAL

    def _restore_interval(self) -> None:
        import src.core.behaviors.socket.heartbeat_behavior as hb_module

        hb_module._HEARTBEAT_INTERVAL_SECONDS = 30

    def test_heartbeat_loop_sends_ping_then_date(self) -> None:
        self._patch_interval()
        try:
            self.behavior.start(callback=None, parent=None)
            # Wait for two full intervals: PingRequest + DateRequest
            threading.Event().wait(timeout=_SHORT_INTERVAL * 3)
            self.behavior.stop()
        finally:
            self._restore_interval()

        types = [type(m) for m in self.sent_messages]
        self.assertIn(PingRequest, types)
        self.assertIn(DateRequest, types)
        ping_idx = next(i for i, t in enumerate(types) if t is PingRequest)
        date_idx = next(i for i, t in enumerate(types) if t is DateRequest)
        self.assertLess(ping_idx, date_idx, "PingRequest must precede DateRequest")

    def test_heartbeat_stops_cleanly_before_first_tick(self) -> None:
        self._patch_interval()
        try:
            self.behavior.start(callback=None, parent=None)
            self.behavior.stop()
        finally:
            self._restore_interval()

        # After immediate stop the loop must not keep sending
        sent_count = len(self.sent_messages)
        threading.Event().wait(timeout=_SHORT_INTERVAL * 2)
        self.assertEqual(len(self.sent_messages), sent_count)

    def test_ping_request_is_quiet(self) -> None:
        self._patch_interval()
        try:
            self.behavior.start(callback=None, parent=None)
            threading.Event().wait(timeout=_SHORT_INTERVAL * 2)
            self.behavior.stop()
        finally:
            self._restore_interval()

        ping_messages = [m for m in self.sent_messages if isinstance(m, PingRequest)]
        self.assertTrue(len(ping_messages) > 0)
        for ping in ping_messages:
            self.assertTrue(ping.quiet)


if __name__ == "__main__":
    unittest.main()
