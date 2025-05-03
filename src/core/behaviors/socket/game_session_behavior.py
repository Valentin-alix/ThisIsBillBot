import secrets
from dataclasses import dataclass, field

from datas.protos.non_obf.game.basic_pb2 import (
    BasicLatencyStatsEvent,
    BasicLatencyStatsRequest,
    SequenceNumberEvent,
    SequenceNumberRequest,
)
from datas.protos.non_obf.game.challenge_pb2 import (
    ChallengeBonusChoiceRequest,
    ChallengeModSelectRequest,
)
from datas.protos.non_obf.game.character_pb2 import PlayerStatusUpdateRequest
from datas.protos.non_obf.game.client_verification_pb2 import (
    ClientChallengeInitRequest,
    ClientChallengeProofRequest,
    ClientIdRequest,
    ServerChallengeEvent,
    ServerSessionReadyEvent,
    ServerVerificationEvent,
)
from datas.protos.non_obf.game.common_pb2 import (
    ChallengeBonus,
    ChallengeMod,
    CharacterStatus,
)
from datas.protos.non_obf.game.context_pb2 import ContextCreationEvent
from datas.protos.non_obf.game.fight_pb2 import (
    FightIsTurnReadyEvent,
    FightTurnReadyRequest,
)
from datas.protos.non_obf.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    SequenceEndEvent,
    SequenceStartEvent,
)
from datas.protos.non_obf.game.gamemap_pb2 import FightMapInformationEvent

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

_ACK_DELAY = (0.10, 0.20)
_TURN_READY_DELAY = (0.10, 0.20)


@dataclass
class GameSessionBehavior(Behavior):
    _cvlg: int = field(init=False, default=0)
    _cvlh: int = field(init=False, default=0)
    _sequence_number: int = field(init=False, default=1)

    _fight_sequence_depth: int = field(init=False, default=0)
    _turn_ready_pending: bool = field(init=False, default=False)
    _player_status_sent: bool = field(init=False, default=False)

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
        self.event_manager.on(
            ContextCreationEvent, self._on_context_creation, originator=self
        )
        self.event_manager.on(
            SequenceStartEvent, self._on_sequence_start, originator=self
        )
        self.event_manager.on(SequenceEndEvent, self._on_sequence_end, originator=self)
        self.event_manager.on(
            FightIsTurnReadyEvent, self._on_fight_is_turn_ready, originator=self
        )
        self.event_manager.on(
            FightMapInformationEvent,
            self._on_fight_map_information,
            originator=self,
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

    def _on_context_creation(self, msg: ContextCreationEvent) -> None:
        if self._player_status_sent:
            return
        self._player_status_sent = True
        self.event_manager.send(
            PlayerStatusUpdateRequest(
                status=CharacterStatus(status=CharacterStatus.Status.STATUS_SOLO)
            )
        )

    def _on_sequence_number(self, msg: SequenceNumberEvent) -> None:
        self.event_manager.send(SequenceNumberRequest(number=self._sequence_number))
        self._sequence_number += 1

    def _on_basic_latency(self, msg: BasicLatencyStatsEvent) -> None:
        self.event_manager.send(BasicLatencyStatsRequest(latency=0))

    def _on_sequence_start(self, msg: SequenceStartEvent) -> None:
        self._fight_sequence_depth += 1

    def _on_sequence_end(self, msg: SequenceEndEvent) -> None:
        self._fight_sequence_depth -= 1
        if self._fight_sequence_depth > 0:
            return
        self._fight_sequence_depth = 0
        self.run_timer(_ACK_DELAY, lambda: self._send_action_ack(msg.action_id))
        if self._turn_ready_pending:
            self._turn_ready_pending = False
            self.run_timer(_TURN_READY_DELAY, self._send_turn_ready)

    def _send_action_ack(self, action_id: int) -> None:
        ack = GameActionAcknowledgementRequest(valid=True, action_id=action_id)
        self.event_manager.send(ack)
        self.event_manager.process_msg(ack)

    def _on_fight_is_turn_ready(self, msg: FightIsTurnReadyEvent) -> None:
        if msg.character_id != self.game_state.player.character_id:
            return
        if self._fight_sequence_depth > 0:
            self._turn_ready_pending = True
            return
        self.run_timer(_TURN_READY_DELAY, self._send_turn_ready)

    def _send_turn_ready(self) -> None:
        self.event_manager.send(FightTurnReadyRequest(is_ready=True))

    def _on_fight_map_information(self, _msg: FightMapInformationEvent) -> None:
        self.event_manager.send(
            ChallengeModSelectRequest(challenge_mod=ChallengeMod.CHALLENGE_CHOICE)
        )
        self.event_manager.send(
            ChallengeBonusChoiceRequest(
                challenge_bonus=ChallengeBonus.CHALLENGE_DROP_BONUS
            )
        )
