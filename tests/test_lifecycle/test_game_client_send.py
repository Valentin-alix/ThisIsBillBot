from typing import cast
from unittest.mock import MagicMock

import pytest
from datas.protos.non_obf.game.game_action_pb2 import GameActionFightCastRequest
from datas.protos.non_obf.game.spell_pb2 import SpellsEvent
from google.protobuf.message import Message

from src.core.bot.bot import Bot
from src.core.socket_network import game_client as game_client_module
from src.core.socket_network.game_client import GameClient


def _fake_obf(*_: object) -> tuple[Message, Message]:
    return cast(Message, MagicMock()), cast(Message, MagicMock())


def _fake_encode(_: Message) -> bytes:
    return b""


@pytest.fixture
def game_client(runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch) -> GameClient:
    client = GameClient(bot=runtime_bot)
    client.client_socket = MagicMock()
    # Le bot est son propre client en socket : on court-circuite l'encodage obfusqué
    # (qui exige le data store runtime) pour isoler le routage send -> process_msg.
    monkeypatch.setattr(game_client_module, "get_obf_game_message_from_msg", _fake_obf)
    monkeypatch.setattr(game_client_module, "encode_msg", _fake_encode)
    return client


class TestGameClientSendRoutesToProcessMsg:
    def test_outgoing_cast_request_records_cast_tracking(
        self, game_client: GameClient, runtime_bot: Bot
    ) -> None:
        """En socket, le message sortant doit repasser par process_msg pour que
        fight_frame.on_game_action_fight_cast_request enregistre le cast (parité
        MITM). Sans ça, les self-buffs one-shot sont relancés en boucle chaque tour.
        """
        runtime_bot.game_state.fight.fight_turn = 5
        runtime_bot.debug_recorder = MagicMock()

        clear_msg = GameActionFightCastRequest(spell_id=13052, cell=42)
        game_client.send_msg(clear_msg)

        fight = runtime_bot.game_state.fight
        assert fight.last_cast_turn_by_spell_id.get(13052) == 5
        assert fight.count_casted_by_spell_id_on_current_turn.get(13052) == 1
        runtime_bot.debug_recorder.record_game_message.assert_called_once()
        recorded_clear_msg = (
            runtime_bot.debug_recorder.record_game_message.call_args.args[0]
        )
        recorded_from_server = (
            runtime_bot.debug_recorder.record_game_message.call_args.args[3]
        )
        assert recorded_clear_msg is clear_msg
        assert recorded_from_server is False

    def test_incoming_socket_message_is_recorded(
        self,
        game_client: GameClient,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        runtime_bot.debug_recorder = MagicMock()
        clear_msg = SpellsEvent(human_spells=[])
        obf_msg = cast(Message, MagicMock())

        def fake_decode_varint_size(msg_datas: bytes) -> tuple[int, int]:
            return 3, 1

        def fake_get_game_msg(*args: object) -> tuple[None, SpellsEvent, Message, int]:
            return None, clear_msg, obf_msg, 42

        monkeypatch.setattr(
            game_client_module, "decode_varint_size", fake_decode_varint_size
        )
        monkeypatch.setattr(
            game_client_module,
            "get_game_msg",
            fake_get_game_msg,
        )

        game_client.on_received_msg_datas(b"\x03abc")

        runtime_bot.debug_recorder.record_game_message.assert_called_once_with(
            clear_msg, obf_msg, 42, True
        )


class TestSocketInterfaceBinding:
    def test_connect_socket_binds_configured_interface(self, runtime_bot: Bot) -> None:
        client = GameClient(bot=runtime_bot, interface_ip="192.168.0.117")
        client.client_socket = MagicMock()

        client.connect_socket("example.invalid", 5555)

        client.client_socket.bind.assert_called_once_with(("192.168.0.117", 0))
        client.client_socket.connect.assert_called_once_with(("example.invalid", 5555))
