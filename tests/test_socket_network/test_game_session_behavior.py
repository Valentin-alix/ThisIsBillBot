import unittest
from collections import defaultdict
from dataclasses import dataclass
from threading import RLock
from unittest.mock import create_autospec

from datas.protos.non_obf.game.basic_pb2 import (
    BasicLatencyStatsEvent,
    BasicLatencyStatsRequest,
    SequenceNumberEvent,
    SequenceNumberRequest,
)
from datas.protos.non_obf.game.client_verification_pb2 import (
    ClientChallengeInitRequest,
    ClientChallengeProofRequest,
    ClientIdRequest,
    ServerChallengeEvent,
    ServerSessionReadyEvent,
    ServerVerificationEvent,
)
from google.protobuf.message import Message

from src.core.behaviors.socket.game_session_behavior import (
    _DH_G,
    _DH_P,
    _DH_Q,
    _LATENCY_MAX,
    _LATENCY_MIN,
    GameSessionBehavior,
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


class GameSessionBehaviorTests(unittest.TestCase):
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

        self.event_manager.send.side_effect = send
        self.event_manager.on.side_effect = on

        self.behavior = GameSessionBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.logger,
        )

    def test_run_registers_all_listeners(self) -> None:
        self.behavior.start(callback=None, parent=None)

        self.assertIn(ServerVerificationEvent, self.listeners_by_type)
        self.assertIn(ServerChallengeEvent, self.listeners_by_type)
        self.assertIn(ServerSessionReadyEvent, self.listeners_by_type)
        self.assertIn(SequenceNumberEvent, self.listeners_by_type)
        self.assertIn(BasicLatencyStatsEvent, self.listeners_by_type)

    def test_server_verification_sends_challenge_init(self) -> None:
        self.behavior._on_server_verification(ServerVerificationEvent())

        self.assertEqual(len(self.sent_messages), 1)
        msg = self.sent_messages[0]
        assert isinstance(msg, ClientChallengeInitRequest)
        challenge_key = int(msg.challenge_key)
        expected = pow(_DH_G, self.behavior._cvlh, _DH_P)
        self.assertEqual(challenge_key, expected)

    def test_server_challenge_with_value_sends_correct_proof(self) -> None:
        self.behavior._cvlg = 12345
        self.behavior._cvlh = 67890
        server_value = "999"

        self.behavior._on_server_challenge(ServerChallengeEvent(value=server_value))

        self.assertEqual(len(self.sent_messages), 1)
        msg = self.sent_messages[0]
        assert isinstance(msg, ClientChallengeProofRequest)
        expected_proof = (67890 + int(server_value) * 12345) % _DH_Q
        self.assertEqual(int(msg.proof), expected_proof)

    def test_server_challenge_without_value_uses_fallback(self) -> None:
        self.behavior._cvlg = 12345
        self.behavior._cvlh = 67890

        self.behavior._on_server_challenge(ServerChallengeEvent())

        self.assertEqual(len(self.sent_messages), 1)
        msg = self.sent_messages[0]
        assert isinstance(msg, ClientChallengeProofRequest)
        expected_proof = (67890 + 12345) % _DH_Q
        self.assertEqual(int(msg.proof), expected_proof)

    def test_server_session_ready_sends_client_id(self) -> None:
        self.behavior._cvlg = 42

        self.behavior._on_server_session_ready(ServerSessionReadyEvent())

        self.assertEqual(len(self.sent_messages), 1)
        msg = self.sent_messages[0]
        assert isinstance(msg, ClientIdRequest)
        expected_id = pow(_DH_G, 42, _DH_P)
        self.assertEqual(int(msg.id), expected_id)

    def test_sequence_number_increments(self) -> None:
        self.behavior._on_sequence_number(SequenceNumberEvent())
        self.behavior._on_sequence_number(SequenceNumberEvent())

        requests = [
            m for m in self.sent_messages if isinstance(m, SequenceNumberRequest)
        ]
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0].number, 1)
        self.assertEqual(requests[1].number, 2)

    def test_basic_latency_responds_in_range(self) -> None:
        for _ in range(20):
            self.sent_messages.clear()
            self.behavior._on_basic_latency(BasicLatencyStatsEvent())
            msg = self.sent_messages[0]
            assert isinstance(msg, BasicLatencyStatsRequest)
            self.assertGreaterEqual(msg.latency, _LATENCY_MIN)
            self.assertLessEqual(msg.latency, _LATENCY_MAX)

    def test_listeners_are_persistent_not_once(self) -> None:
        self.behavior.start(callback=None, parent=None)

        for msg_type in (
            ServerVerificationEvent,
            ServerChallengeEvent,
            ServerSessionReadyEvent,
            SequenceNumberEvent,
            BasicLatencyStatsEvent,
        ):
            for listener in self.listeners_by_type[msg_type]:
                self.assertFalse(
                    listener.once,
                    f"{msg_type.__name__} listener should not be once=True",
                )


if __name__ == "__main__":
    unittest.main()
