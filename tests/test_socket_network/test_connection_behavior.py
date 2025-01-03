import unittest
from collections import defaultdict
from dataclasses import dataclass
from threading import RLock
from unittest.mock import create_autospec

from datas.protos.non_obf.connection.login_message_pb2 import (
    CharacterInformation,
    IdentificationRequest,
    IdentificationResponse,
    LoginMessage,
    SelectServerRequest,
    SelectServerResponse,
    Server,
    ServerInformation,
    ServerList,
)
from google.protobuf.message import Message

from src.core.behaviors.socket.connection_behavior import (
    ConnectionBehavior,
)
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


def _make_success_response(server_id: int) -> IdentificationResponse:
    server_list = ServerList(
        servers=[
            ServerInformation(
                server=Server(id=server_id),
                characters=[CharacterInformation(name="char1")],
            )
        ]
    )
    return IdentificationResponse(
        success=IdentificationResponse.Success(server_list=server_list)
    )


class ConnectionBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sent_connection_messages: list[Message] = []
        self.listeners_by_type: defaultdict[type[Message], list[RegisteredListener]] = (
            defaultdict(list)
        )
        self.event_manager = create_autospec(EventManager, instance=True)
        self.game_state = create_autospec(GameState, instance=True)
        self.logger = create_autospec(Logger, instance=True)
        self.event_manager.lock = RLock()

        def send_connection_msg(msg: Message) -> None:
            self.sent_connection_messages.append(msg)

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

        self.event_manager.send_connection_msg.side_effect = send_connection_msg
        self.event_manager.on.side_effect = on
        self.event_manager.clear_listener_by_origin.side_effect = (
            clear_listener_by_origin
        )
        self.event_manager.clear_modifier_by_origin.side_effect = (
            clear_modifier_by_origin
        )

        self.behavior = ConnectionBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.logger,
        )

    def _start(self, game_token: str = "test-token") -> None:
        self.behavior.start(callback=None, parent=None, game_token=game_token)

    def _get_identification_request(self) -> IdentificationRequest:
        self.assertEqual(len(self.sent_connection_messages), 1)
        msg = self.sent_connection_messages[0]
        assert isinstance(msg, LoginMessage)
        return msg.request.identification

    def test_connect_sends_login_message_with_uuid_zero(self) -> None:
        self._start("my-token")

        self.assertEqual(len(self.sent_connection_messages), 1)
        msg = self.sent_connection_messages[0]
        assert isinstance(msg, LoginMessage)
        self.assertEqual(msg.request.uuid, "0")

    def test_connect_sends_identification_request_with_token(self) -> None:
        self._start("my-token")

        identification = self._get_identification_request()
        self.assertEqual(identification.tokenRequest.token, "my-token")

    def test_connect_identification_request_has_shield(self) -> None:
        self._start("my-token")

        identification = self._get_identification_request()
        self.assertTrue(identification.tokenRequest.HasField("shield"))
        self.assertEqual(identification.tokenRequest.shield.certificateId, 0)
        self.assertEqual(identification.tokenRequest.shield.certificateHash, "")

    def test_connect_registers_identification_response_listener(self) -> None:
        self._start()

        self.assertIn(IdentificationResponse, self.listeners_by_type)
        listener = self.listeners_by_type[IdentificationResponse][0]
        self.assertTrue(listener.once)

    def test_on_identification_response_success_sends_select_server_with_uuid_one(
        self,
    ) -> None:
        self._start()

        self.behavior.on_identification_response(_make_success_response(42))

        self.assertEqual(len(self.sent_connection_messages), 2)
        second_msg = self.sent_connection_messages[1]
        assert isinstance(second_msg, LoginMessage)
        self.assertEqual(second_msg.request.uuid, "1")
        select_server: SelectServerRequest = second_msg.request.selectServer
        self.assertEqual(select_server.server, 42)

    def test_on_identification_response_success_registers_select_server_listener(
        self,
    ) -> None:
        self._start()

        self.behavior.on_identification_response(_make_success_response(1))

        self.assertIn(SelectServerResponse, self.listeners_by_type)

    def test_on_select_server_response_success_calls_finish_with_server_info(
        self,
    ) -> None:
        self._start()
        finished_args: list[tuple[object, ...]] = []
        self.behavior.callback = lambda *args: finished_args.append(args)

        success = SelectServerResponse.Success(
            host="game.server.com", ports=[5555], token="game-token"
        )
        self.behavior.on_select_server_response(SelectServerResponse(success=success))

        self.assertEqual(len(finished_args), 1)
        error_code, host, port, token = finished_args[0]
        self.assertIsNone(error_code)
        self.assertEqual(host, "game.server.com")
        self.assertEqual(port, 5555)
        self.assertEqual(token, "game-token")


if __name__ == "__main__":
    unittest.main()
