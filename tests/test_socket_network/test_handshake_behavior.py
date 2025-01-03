import unittest
from collections import defaultdict
from dataclasses import dataclass
from threading import RLock
from unittest.mock import create_autospec

from datas.protos.non_obf.game.bak_pb2 import BakApiTokenRequest
from datas.protos.non_obf.game.character_management_pb2 import (
    CharacterListEvent,
    CharacterListRequest,
    CharacterLoadingCompleteEvent,
    CharacterSelectionRequest,
)
from datas.protos.non_obf.game.chat_pb2 import SubscribeMultipleChannelRequest
from datas.protos.non_obf.game.common_pb2 import Character
from datas.protos.non_obf.game.connection_pb2 import (
    AuthenticationTicketAcceptedEvent,
    IdentificationRequest as GameIdentificationRequest,
)
from datas.protos.non_obf.game.context_pb2 import ContextCreationRequest
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

        def clear_modifier_by_origin(_originator: object) -> None:
            return None

        self.event_manager.send.side_effect = send
        self.event_manager.on.side_effect = on
        self.event_manager.clear_listener_by_origin.side_effect = (
            clear_listener_by_origin
        )
        self.event_manager.clear_modifier_by_origin.side_effect = (
            clear_modifier_by_origin
        )

        self.behavior = HandshakeBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.logger,
        )

    def test_start_sends_identification_request(self) -> None:
        self.behavior.start(ticket="my-ticket", callback=None, parent=None)

        self.assertEqual(self.behavior.state, BehaviorState.RUNNING)
        self.assertEqual(len(self.sent_messages), 1)
        sent_message = self.sent_messages[0]
        assert isinstance(sent_message, GameIdentificationRequest)
        self.assertEqual(sent_message.ticket_key, "my-ticket")
        self.assertEqual(sent_message.language_code, "fr")
        self.assertIn(AuthenticationTicketAcceptedEvent, self.listeners_by_type)
        self.assertNotIn(CharacterListEvent, self.listeners_by_type)

    def test_authentication_ticket_accepted_sends_character_list_and_bak_token(
        self,
    ) -> None:
        self.behavior.on_authentication_ticket_accepted_event(
            AuthenticationTicketAcceptedEvent()
        )

        types = [type(m) for m in self.sent_messages]
        self.assertIn(CharacterListRequest, types)
        self.assertIn(BakApiTokenRequest, types)
        self.assertIn(CharacterListEvent, self.listeners_by_type)

    def test_character_list_selects_first_character_twice(self) -> None:
        message = CharacterListEvent(characters=[Character(id=42), Character(id=99)])

        self.behavior.on_character_list_event(message)

        selection_messages = [
            m for m in self.sent_messages if isinstance(m, CharacterSelectionRequest)
        ]
        self.assertEqual(len(selection_messages), 2)
        self.assertEqual(selection_messages[0].character_id, 42)
        self.assertEqual(selection_messages[1].character_id, 42)
        self.assertIn(CharacterLoadingCompleteEvent, self.listeners_by_type)

    def test_character_loading_complete_sends_context_creation_and_subscribe(
        self,
    ) -> None:
        self.behavior.on_character_loading_complete_event(
            CharacterLoadingCompleteEvent()
        )

        types = [type(m) for m in self.sent_messages]
        self.assertIn(ContextCreationRequest, types)
        self.assertIn(SubscribeMultipleChannelRequest, types)

    def test_character_loading_complete_finishes_behavior(self) -> None:
        self.behavior.start(ticket="ticket", callback=None, parent=None)
        self.behavior.on_authentication_ticket_accepted_event(
            AuthenticationTicketAcceptedEvent()
        )
        self.behavior.on_character_list_event(
            CharacterListEvent(characters=[Character(id=1)])
        )

        self.behavior.on_character_loading_complete_event(
            CharacterLoadingCompleteEvent()
        )

        self.assertEqual(self.behavior.state, BehaviorState.STOPPED)

    def test_character_list_without_characters_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "has no characters"):
            self.behavior.on_character_list_event(CharacterListEvent())

    def test_subscribe_channels_are_not_empty(self) -> None:
        self.behavior.on_character_loading_complete_event(
            CharacterLoadingCompleteEvent()
        )

        subscribe_msgs = [
            m
            for m in self.sent_messages
            if isinstance(m, SubscribeMultipleChannelRequest)
        ]
        self.assertEqual(len(subscribe_msgs), 1)
        self.assertGreater(len(subscribe_msgs[0].channel_enabled), 0)


if __name__ == "__main__":
    unittest.main()
