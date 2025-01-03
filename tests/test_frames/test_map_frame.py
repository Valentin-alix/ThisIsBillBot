import unittest
from threading import Event, RLock
from unittest.mock import Mock, create_autospec

from datas.protos.non_obf.game.character_pb2 import PlayerStatusUpdateRequest
from datas.protos.non_obf.game.common_pb2 import CharacterStatus
from datas.protos.non_obf.game.context_pb2 import (
    ContextCreationEvent,
    ContextReadyRequest,
)
from datas.protos.non_obf.game.gamemap_pb2 import MapCurrentEvent, MapInformationRequest
from google.protobuf.message import Message

from src.core.events_manager.event_manager import EventManager
from src.core.frames.map_frame import MapFrame
from src.services.logging.logger import Logger


def _make_frame(is_socket_mode: bool = True) -> tuple[MapFrame, list[Message]]:
    sent_messages: list[Message] = []
    event_manager = create_autospec(EventManager, instance=True)
    event_manager.lock = RLock()
    event_manager.is_socket_mode = is_socket_mode
    event_manager.send.side_effect = sent_messages.append

    frame = MapFrame(
        event_manager=event_manager,
        game_state=Mock(),
        game_info_signals=Mock(),
        inventory_signals=Mock(),
        is_playing_event=Event(),
        world_signals=Mock(),
        _logger=create_autospec(Logger, instance=True),
    )
    return frame, sent_messages


class MapFrameSocketModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame, self.sent_messages = _make_frame(is_socket_mode=True)

    def test_map_current_sends_map_information_request(self) -> None:
        self.frame.on_map_current_event(MapCurrentEvent(map_id=42))

        types = [type(m) for m in self.sent_messages]
        self.assertIn(MapInformationRequest, types)
        req = next(
            m for m in self.sent_messages if isinstance(m, MapInformationRequest)
        )
        self.assertEqual(req.map_id, 42)

    def test_map_current_does_not_send_context_ready_by_default(self) -> None:
        self.frame.on_map_current_event(MapCurrentEvent(map_id=42))

        types = [type(m) for m in self.sent_messages]
        self.assertNotIn(ContextReadyRequest, types)

    def test_context_creation_sends_player_status_solo(self) -> None:
        self.frame.on_context_creation_event(
            ContextCreationEvent(context=ContextCreationEvent.GameContext.ROLE_PLAY)
        )

        self.assertEqual(len(self.sent_messages), 1)
        msg = self.sent_messages[0]
        assert isinstance(msg, PlayerStatusUpdateRequest)
        self.assertEqual(msg.status.status, CharacterStatus.Status.STATUS_SOLO)

    def test_context_creation_fight_sets_need_context_ready(self) -> None:
        self.assertFalse(self.frame._need_context_ready)

        self.frame.on_context_creation_event(
            ContextCreationEvent(context=ContextCreationEvent.GameContext.FIGHT)
        )

        self.assertTrue(self.frame._need_context_ready)

    def test_context_creation_role_play_does_not_set_need_context_ready(self) -> None:
        self.frame.on_context_creation_event(
            ContextCreationEvent(context=ContextCreationEvent.GameContext.ROLE_PLAY)
        )

        self.assertFalse(self.frame._need_context_ready)

    def test_map_current_sends_context_ready_when_flag_set(self) -> None:
        self.frame._need_context_ready = True

        self.frame.on_map_current_event(MapCurrentEvent(map_id=99))

        types = [type(m) for m in self.sent_messages]
        self.assertIn(ContextReadyRequest, types)
        req = next(m for m in self.sent_messages if isinstance(m, ContextReadyRequest))
        self.assertEqual(req.map_id, 99)

    def test_context_ready_flag_reset_after_send(self) -> None:
        self.frame._need_context_ready = True

        self.frame.on_map_current_event(MapCurrentEvent(map_id=1))

        self.assertFalse(self.frame._need_context_ready)

    def test_second_map_current_does_not_resend_context_ready(self) -> None:
        self.frame._need_context_ready = True
        self.frame.on_map_current_event(MapCurrentEvent(map_id=1))
        self.sent_messages.clear()

        self.frame.on_map_current_event(MapCurrentEvent(map_id=2))

        types = [type(m) for m in self.sent_messages]
        self.assertNotIn(ContextReadyRequest, types)


class MapFrameMitmModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame, self.sent_messages = _make_frame(is_socket_mode=False)

    def test_map_current_does_not_send_any_message(self) -> None:
        self.frame.on_map_current_event(MapCurrentEvent(map_id=42))

        self.assertEqual(len(self.sent_messages), 0)

    def test_context_creation_does_not_send_player_status(self) -> None:
        self.frame.on_context_creation_event(
            ContextCreationEvent(context=ContextCreationEvent.GameContext.ROLE_PLAY)
        )

        self.assertEqual(len(self.sent_messages), 0)

    def test_context_creation_fight_still_sets_need_context_ready(self) -> None:
        self.frame.on_context_creation_event(
            ContextCreationEvent(context=ContextCreationEvent.GameContext.FIGHT)
        )

        self.assertTrue(self.frame._need_context_ready)

    def test_map_current_does_not_send_context_ready_even_when_flag_set(self) -> None:
        self.frame._need_context_ready = True

        self.frame.on_map_current_event(MapCurrentEvent(map_id=99))

        self.assertEqual(len(self.sent_messages), 0)


if __name__ == "__main__":
    unittest.main()
