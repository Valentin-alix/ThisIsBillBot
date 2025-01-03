import random
import secrets
from dataclasses import dataclass, field

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

from src.core.behaviors.behavior import Behavior

# RFC 2409 768-bit MODP Group 1 (public parameters)
_DH_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
    "C90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA6"
    "3B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F1437"
    "4FE1356D6D51C245E485B576625E7EC6F44C42E9A63A3620FFFFFFFFFFFFFFFF",
    16,
)
_DH_G = 2
_DH_Q = (_DH_P - 1) // 2

_LATENCY_MIN = 500
_LATENCY_MAX = 650


@dataclass
class GameSessionBehavior(Behavior):
    _cvlg: int = field(init=False, default=0)
    _cvlh: int = field(init=False, default=0)
    _sequence_number: int = field(init=False, default=1)

    def run(self) -> None:
        self.event_manager.on(
            ServerVerificationEvent, self._on_server_verification, originator=self
        )
        self.event_manager.on(
            ServerChallengeEvent, self._on_server_challenge, originator=self
        )
        self.event_manager.on(
            ServerSessionReadyEvent, self._on_server_session_ready, originator=self
        )
        self.event_manager.on(
            SequenceNumberEvent, self._on_sequence_number, originator=self
        )
        self.event_manager.on(
            BasicLatencyStatsEvent, self._on_basic_latency, originator=self
        )

    def _on_server_verification(self, _msg: ServerVerificationEvent) -> None:
        self._cvlg = secrets.randbits(512) % _DH_P
        self._cvlh = secrets.randbits(400)
        challenge_key = pow(_DH_G, self._cvlh, _DH_P)
        self.event_manager.send(
            ClientChallengeInitRequest(challenge_key=str(challenge_key))
        )

    def _on_server_challenge(self, msg: ServerChallengeEvent) -> None:
        if msg.HasField("value") and msg.value:
            proof = (self._cvlh + int(msg.value) * self._cvlg) % _DH_Q
        else:
            proof = (self._cvlh + self._cvlg) % _DH_Q
        if proof < 0:
            proof += _DH_Q
        self.event_manager.send(ClientChallengeProofRequest(proof=str(proof)))

    def _on_server_session_ready(self, _msg: ServerSessionReadyEvent) -> None:
        client_id = pow(_DH_G, self._cvlg, _DH_P)
        self.event_manager.send(ClientIdRequest(id=str(client_id)))

    def _on_sequence_number(self, msg: SequenceNumberEvent) -> None:
        self.event_manager.send(SequenceNumberRequest(number=self._sequence_number))
        self._sequence_number += 1

    def _on_basic_latency(self, msg: BasicLatencyStatsEvent) -> None:
        self.event_manager.send(
            BasicLatencyStatsRequest(latency=random.randint(_LATENCY_MIN, _LATENCY_MAX))
        )
