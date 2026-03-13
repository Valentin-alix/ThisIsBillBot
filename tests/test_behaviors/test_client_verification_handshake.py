import hashlib
from dataclasses import dataclass
from typing import cast

import pytest
from DBDofusUnity.datas.protos.non_obf.game.client_verification_pb2 import (
    ClientChallengeInitRequest,
    ClientChallengeProofRequest,
    ClientIdRequest,
    ServerChallengeEvent,
    ServerSessionReadyEvent,
    ServerVerificationEvent,
)
from google.protobuf.message import Message

from src.core.behaviors.socket import game_session_behavior as game_session_module
from src.core.behaviors.socket.game_session_behavior import _DH_G, _DH_P, _DH_Q
from src.core.bot.bot import Bot


_SERVER_CHALLENGE = "87989774959674335681374014435310768134220535430930660942639414008177554728153"
_FAKE_HWID = "1B4F0E9851971998E732078544C96B36C3D01CEDF7CAA332359D6F1D83567014"


@dataclass
class _FakeBotConfig:
    hardware_id: str


class _FakeBotConfigService:
    def get_bot_config(self, login: str) -> _FakeBotConfig:
        del login
        return _FakeBotConfig(hardware_id=_FAKE_HWID)


def _proof_verifies(public_key: int, commitment: int, challenge: int, proof: int) -> bool:
    return pow(_DH_G, proof, _DH_P) == (commitment * pow(public_key, challenge, _DH_P)) % _DH_P


def _only(sent_messages: list[Message], msg_type: type[Message]) -> Message:
    matching = [msg for msg in sent_messages if isinstance(msg, msg_type)]
    assert len(matching) == 1, f"expected exactly one {msg_type.__name__}, got {len(matching)}"
    return matching[0]


class TestClientVerificationHandshake:
    def test_dh_group_is_rfc2409_first_oakley_group(self) -> None:
        assert _DH_P.bit_length() == 768
        assert _DH_G == 2
        assert _DH_Q == (_DH_P - 1) // 2

        assert pow(_DH_G, _DH_Q, _DH_P) == 1

    def test_server_supplied_challenge_produces_a_verifiable_proof(
        self,
        runtime_bot: Bot,
    ) -> None:
        sent_messages: list[Message] = []
        runtime_bot.event_manager.on_send_game_callback = sent_messages.append

        runtime_bot.game_session_behavior.run()
        runtime_bot.event_manager.process_msg(ServerVerificationEvent())
        runtime_bot.event_manager.process_msg(ServerSessionReadyEvent())
        runtime_bot.event_manager.process_msg(ServerChallengeEvent(value=_SERVER_CHALLENGE))

        init_request = cast(ClientChallengeInitRequest, _only(sent_messages, ClientChallengeInitRequest))
        id_request = cast(ClientIdRequest, _only(sent_messages, ClientIdRequest))
        proof_request = cast(ClientChallengeProofRequest, _only(sent_messages, ClientChallengeProofRequest))

        assert _proof_verifies(
            public_key=int(init_request.challenge_key),
            commitment=int(id_request.id),
            challenge=int(_SERVER_CHALLENGE),
            proof=int(proof_request.proof),
        )

    def test_omitted_challenge_falls_back_to_device_bound_transcript(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(game_session_module, "BotConfigService", _FakeBotConfigService)
        sent_messages: list[Message] = []
        runtime_bot.event_manager.on_send_game_callback = sent_messages.append

        runtime_bot.game_session_behavior.run()
        runtime_bot.event_manager.process_msg(ServerVerificationEvent())
        runtime_bot.event_manager.process_msg(ServerSessionReadyEvent())
        runtime_bot.event_manager.process_msg(ServerChallengeEvent())

        init_request = cast(ClientChallengeInitRequest, _only(sent_messages, ClientChallengeInitRequest))
        id_request = cast(ClientIdRequest, _only(sent_messages, ClientIdRequest))
        proof_request = cast(ClientChallengeProofRequest, _only(sent_messages, ClientChallengeProofRequest))

        public_key = int(init_request.challenge_key)
        commitment = int(id_request.id)
        transcript = f"{_DH_G}{public_key}{commitment}{_FAKE_HWID}"
        challenge = int.from_bytes(hashlib.sha256(transcript.encode("utf-8")).digest(), "big")

        assert _proof_verifies(
            public_key=public_key,
            commitment=commitment,
            challenge=challenge,
            proof=int(proof_request.proof),
        )

    def test_commitment_is_regenerated_on_every_session_ready(self, runtime_bot: Bot) -> None:
        sent_messages: list[Message] = []
        runtime_bot.event_manager.on_send_game_callback = sent_messages.append

        runtime_bot.game_session_behavior.run()
        runtime_bot.event_manager.process_msg(ServerVerificationEvent())
        runtime_bot.event_manager.process_msg(ServerSessionReadyEvent())
        runtime_bot.event_manager.process_msg(ServerChallengeEvent(value=_SERVER_CHALLENGE))
        runtime_bot.event_manager.process_msg(ServerSessionReadyEvent())
        runtime_bot.event_manager.process_msg(ServerChallengeEvent(value=_SERVER_CHALLENGE))

        id_requests = [msg for msg in sent_messages if isinstance(msg, ClientIdRequest)]
        init_requests = [msg for msg in sent_messages if isinstance(msg, ClientChallengeInitRequest)]
        proof_requests = [msg for msg in sent_messages if isinstance(msg, ClientChallengeProofRequest)]

        assert len(id_requests) == 2
        assert id_requests[0].id != id_requests[1].id, "reused commitment leaks the secret"
        assert len(proof_requests) == 2
        assert proof_requests[0].proof != proof_requests[1].proof

        public_key = int(init_requests[0].challenge_key)
        for id_request, proof_request in zip(id_requests, proof_requests, strict=True):
            assert _proof_verifies(
                public_key=public_key,
                commitment=int(id_request.id),
                challenge=int(_SERVER_CHALLENGE),
                proof=int(proof_request.proof),
            )
