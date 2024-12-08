import unittest
from collections import defaultdict
from dataclasses import dataclass
from threading import RLock
from unittest.mock import create_autospec

from datas.protos.non_obf.game.character_management_pb2 import (
    CharacterForceSelectionEvent,
    CharacterForceSelectionReadyRequest,
    CharacterListEvent,
    CharacterListRequest,
    CharacterLoadingCompleteEvent,
    CharacterSelectionEvent,
    CharacterSelectionRequest,
)
from datas.protos.non_obf.game.common_pb2 import Character
from datas.protos.non_obf.game.connection_pb2 import (
    AuthenticationTicketAcceptedEvent,
    IdentificationRequest as GameIdentificationRequest,
)
from datas.protos.non_obf.game.context_pb2 import (
    ContextCreationRequest,
    ContextReadyRequest,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    MapCurrentEvent,
    MapCurrentInstanceEvent,
)
from google.protobuf.message import Message

from src.core.behaviors.behavior import BehaviorState
from src.core.behaviors.socket.handshake_behavior import HandshakeBehavior
from src.core.events_manager.event_manager import EventManager
from src.core.events_manager.priority import PriorityEnum
from src.core.states.game_state import GameState
from src.services.logging.logger import Logger


@dataclass
class RegisteredListener:
    callback: object
    once: bool
    originator: object
    priority: PriorityEnum


class HandshakeBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sent_messages: list[Message] = []
        self.listeners_by_type: defaultdict[type[Message], list[RegisteredListener]] = (
            defaultdict(list)
        )
        self.event_manager = create_autospec(EventManager, instance=True)
        self.game_state = create_autospec(GameState, instance=True)
        self.logger = create_autospec(Logger, instance=True)
        self.event_manager.lock = RLock()

        def send(msg: Message) -> None:
            self.sent_messages.append(msg)

        def on(
            msg_type: type[Message],
            callback: object,
            originator: object,
            once: bool = False,
            priority: PriorityEnum = PriorityEnum.NORMAL,
        ) -> None:
            self.listeners_by_type[msg_type].append(
                RegisteredListener(
                    callback=callback,
                    once=once,
                    originator=originator,
                    priority=priority,
                )
            )

        def clear_listener_by_origin(originator: object) -> None:
            for msg_type in list(self.listeners_by_type):
                listeners = [
                    listener
                    for listener in self.listeners_by_type[msg_type]
                    if listener.originator != originator
                ]
                if listeners:
                    self.listeners_by_type[msg_type] = listeners
                else:
                    del self.listeners_by_type[msg_type]

        self.event_manager.send.side_effect = send
        self.event_manager.on.side_effect = on
        self.event_manager.clear_listener_by_origin.side_effect = (
            clear_listener_by_origin
        )

        def clear_modifier_by_origin(_originator: object) -> None:
            return None

        self.event_manager.clear_modifier_by_origin.side_effect = (
            clear_modifier_by_origin
        )

        self.behavior = HandshakeBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.logger,
        )

    def test_start_registers_listeners_and_sends_identification_request(self) -> None:
        self.behavior.start(ticket="ticket", callback=None, parent=None)

        self.assertEqual(self.behavior.state, BehaviorState.RUNNING)
        self.assertEqual(len(self.sent_messages), 1)
        sent_message = self.sent_messages[0]
        assert isinstance(sent_message, GameIdentificationRequest)
        self.assertEqual(sent_message.ticket_key, "ticket")
        self.assertEqual(sent_message.language_code, "fr")
        self.assertIn(AuthenticationTicketAcceptedEvent, self.listeners_by_type)
        self.assertIn(CharacterListEvent, self.listeners_by_type)
        self.assertIn(CharacterLoadingCompleteEvent, self.listeners_by_type)
        self.assertIn(MapCurrentEvent, self.listeners_by_type)
        self.assertIn(MapCurrentInstanceEvent, self.listeners_by_type)

    def test_authentication_ticket_accepted_requests_character_list(self) -> None:
        self.behavior.on_authentication_ticket_accepted_event(
            AuthenticationTicketAcceptedEvent()
        )

        self.assertEqual(len(self.sent_messages), 1)
        assert isinstance(self.sent_messages[0], CharacterListRequest)

    def test_character_list_selects_first_character(self) -> None:
        message = CharacterListEvent(characters=[Character(id=42), Character(id=99)])

        self.behavior.on_character_list_event(message)

        self.assertEqual(len(self.sent_messages), 1)
        sent_message = self.sent_messages[0]
        assert isinstance(sent_message, CharacterSelectionRequest)
        self.assertEqual(sent_message.character_id, 42)

    def test_character_list_without_characters_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "has no characters"):
            self.behavior.on_character_list_event(CharacterListEvent())

    def test_character_force_selection_sends_ready_request(self) -> None:
        self.behavior.on_character_force_selection_event(
            CharacterForceSelectionEvent(character_id=42)
        )

        self.assertEqual(len(self.sent_messages), 1)
        assert isinstance(self.sent_messages[0], CharacterForceSelectionReadyRequest)

    def test_character_selection_error_raises(self) -> None:
        message = CharacterSelectionEvent()
        message.error.SetInParent()

        with self.assertRaisesRegex(ValueError, "failed"):
            self.behavior.on_character_selection_event(message)

    def test_character_loading_complete_requests_context_creation(self) -> None:
        self.behavior.on_character_loading_complete_event(
            CharacterLoadingCompleteEvent()
        )

        self.assertEqual(len(self.sent_messages), 1)
        assert isinstance(self.sent_messages[0], ContextCreationRequest)

    def test_map_current_after_loading_sends_context_ready_and_finishes(self) -> None:
        self.behavior.start(ticket="ticket", callback=None, parent=None)
        self.behavior.on_character_loading_complete_event(
            CharacterLoadingCompleteEvent()
        )
        self.behavior.on_map_current_event(MapCurrentEvent(map_id=12345))

        self.assertEqual(len(self.sent_messages), 3)
        sent_message = self.sent_messages[2]
        assert isinstance(sent_message, ContextReadyRequest)
        self.assertEqual(sent_message.map_id, 12345)
        self.assertEqual(self.behavior.state, BehaviorState.STOPPED)

    def test_map_current_instance_after_loading_sends_context_ready(self) -> None:
        self.behavior.start(ticket="ticket", callback=None, parent=None)
        self.behavior.on_character_loading_complete_event(
            CharacterLoadingCompleteEvent()
        )
        self.behavior.on_map_current_instance_event(
            MapCurrentInstanceEvent(map_id=12345, instantiate_map_id=67890)
        )

        self.assertEqual(len(self.sent_messages), 3)
        sent_message = self.sent_messages[2]
        assert isinstance(sent_message, ContextReadyRequest)
        self.assertEqual(sent_message.map_id, 12345)

    def test_context_ready_waits_for_loading_when_map_arrives_first(self) -> None:
        self.behavior.start(ticket="ticket", callback=None, parent=None)
        self.behavior.on_map_current_event(MapCurrentEvent(map_id=12345))

        self.assertEqual(len(self.sent_messages), 1)

        self.behavior.on_character_loading_complete_event(
            CharacterLoadingCompleteEvent()
        )

        self.assertEqual(len(self.sent_messages), 3)
        sent_message = self.sent_messages[2]
        assert isinstance(sent_message, ContextReadyRequest)
        self.assertEqual(sent_message.map_id, 12345)

    def test_context_ready_is_sent_only_once(self) -> None:
        self.behavior.start(ticket="ticket", callback=None, parent=None)
        self.behavior.on_character_loading_complete_event(
            CharacterLoadingCompleteEvent()
        )
        self.behavior.on_map_current_event(MapCurrentEvent(map_id=12345))
        self.behavior.on_map_current_instance_event(
            MapCurrentInstanceEvent(map_id=54321, instantiate_map_id=67890)
        )

        sent_context_ready = [
            msg for msg in self.sent_messages if isinstance(msg, ContextReadyRequest)
        ]
        self.assertEqual(len(sent_context_ready), 1)
        self.assertEqual(sent_context_ready[0].map_id, 12345)


if __name__ == "__main__":
    unittest.main()
