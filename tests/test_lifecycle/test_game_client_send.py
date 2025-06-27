from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

import pytest
from datas.protos.non_obf.connection.login_message_pb2 import IdentificationResponse
from datas.protos.non_obf.game.connection_pb2 import (
    AuthenticationTicketAcceptedEvent,
)
from datas.protos.non_obf.game.connection_pb2 import (
    IdentificationRequest as GameIdentificationRequest,
)
from datas.protos.non_obf.game.game_action_pb2 import GameActionFightCastRequest
from datas.protos.non_obf.game.spell_pb2 import SpellsEvent
from google.protobuf.message import Message

from src.core.bot.bot import Bot
from src.core.behaviors.socket import connection_behavior as connection_behavior_module
from src.core.behaviors.socket.connection_behavior import ConnectionBehavior
from src.core.socket_network import base_client as base_client_module
from src.core.socket_network import game_client as game_client_module
from src.core.socket_network import socket_client as socket_client_module
from src.core.socket_network.game_client import GameClient
from src.core.socket_network.socket_client import SocketClient
from tests.fixtures.entities import make_actor


def _fake_obf(*_: object) -> tuple[Message, Message]:
    return cast(Message, MagicMock()), cast(Message, MagicMock())


def _fake_encode(_: Message) -> bytes:
    return b""


@pytest.fixture
def game_client(runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch) -> GameClient:
    client = GameClient(bot=runtime_bot, proxy_url="socks5://127.0.0.1:1080")
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

    def test_handshake_timeout_disconnects_game_socket(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        event_manager_on = MagicMock()
        event_manager_send = MagicMock()
        request_disconnect = MagicMock()
        runtime_bot.event_manager.request_disconnect_callback = request_disconnect
        monkeypatch.setattr(runtime_bot.event_manager, "on", event_manager_on)
        monkeypatch.setattr(runtime_bot.event_manager, "send", event_manager_send)

        runtime_bot.handshake_behavior.run("game-ticket")

        event_manager_on.assert_called_once()
        listener_args = event_manager_on.call_args.args
        listener_kwargs = cast(dict[str, object], event_manager_on.call_args.kwargs)
        assert listener_args[0] is AuthenticationTicketAcceptedEvent
        assert listener_kwargs["timeout"] == 15.0
        on_timeout = listener_kwargs["on_timeout"]
        assert callable(on_timeout)

        cast(Callable[[], None], on_timeout)()

        request_disconnect.assert_called_once_with()
        sent_message = event_manager_send.call_args.args[0]
        assert isinstance(sent_message, GameIdentificationRequest)


class TestSocketProxyConnection:
    def test_disconnect_clears_connection_scoped_runtime_state(
        self, runtime_bot: Bot
    ) -> None:
        runtime_bot.game_state.player.character_id = 123
        runtime_bot.game_state.player.character_name = "Renaissance"
        runtime_bot.game_state.map.map_id = 88090898
        runtime_bot.game_state.map.is_in_map_transition = True
        runtime_bot.game_state.fight.in_fight = True
        runtime_bot.game_state.fight.fight_turn = 7
        runtime_bot.game_state.entity.set_actor(make_actor(actor_id=123, cell_id=245))

        runtime_bot.connection_handler.on_disconnected()

        assert runtime_bot.game_state.map.map_id == 0
        assert runtime_bot.game_state.map.is_in_map_transition is False
        assert runtime_bot.game_state.fight.in_fight is False
        assert runtime_bot.game_state.fight.fight_turn == 0
        assert runtime_bot.game_state.entity.actor_by_id == {}
        assert runtime_bot.game_state.player.character_id == 123
        assert runtime_bot.game_state.player.character_name == "Renaissance"

    def test_identification_success_resets_runtime_capture_sequence(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        runtime_store = MagicMock()
        runtime_store_factory = MagicMock(return_value=runtime_store)
        subscription_storage = MagicMock()
        subscription_storage_factory = MagicMock(return_value=subscription_storage)
        runtime_bot.event_manager.on_send_conn_callback = MagicMock()
        connection_behavior = ConnectionBehavior(
            _logger=MagicMock(),
            event_manager=runtime_bot.event_manager,
            game_state=runtime_bot.game_state,
        )
        response = IdentificationResponse(
            success=IdentificationResponse.Success(
                subscription_end_date="2030-01-01T00:00:00"
            )
        )

        monkeypatch.setattr(
            connection_behavior_module, "RuntimeDataStore", runtime_store_factory
        )
        monkeypatch.setattr(
            connection_behavior_module,
            "SubscriptionExpirationStorage",
            subscription_storage_factory,
        )

        connection_behavior.on_identification_response(response)

        runtime_store.start_connection_capture_sequence.assert_called_once_with()
        subscription_storage.record_expiration.assert_called_once()
        runtime_bot.event_manager.on_send_conn_callback.assert_called_once()

    def test_socket_runtime_uses_socks_proxy_for_token_and_connection(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        haapi_calls: list[dict[str, object]] = []
        connection_client_calls: list[dict[str, object]] = []

        class FakeHaapi:
            def __init__(
                self, api_key: str, login: str, proxy_url: str | None = None
            ) -> None:
                haapi_calls.append(
                    {"api_key": api_key, "login": login, "proxy_url": proxy_url}
                )

            def createToken(self, game_id: int, certificate: object) -> str:
                haapi_calls.append(
                    {"game_id": game_id, "certificate": certificate is not None}
                )
                return "game-token"

        class FakeConnectionClient:
            def __init__(
                self,
                bot: Bot,
                connection_behavior: object,
                proxy_url: str | None,
            ) -> None:
                connection_client_calls.append(
                    {
                        "bot": bot,
                        "connection_behavior": connection_behavior,
                        "proxy_url": proxy_url,
                    }
                )

            def connect(self, game_token: str, callback: object) -> None:
                connection_client_calls.append(
                    {"game_token": game_token, "callback": callback}
                )

        monkeypatch.setattr(socket_client_module, "Haapi", FakeHaapi)
        monkeypatch.setattr(
            socket_client_module, "ConnectionClient", FakeConnectionClient
        )

        SocketClient(
            bot=runtime_bot,
            bot_config=MagicMock(),
            socks_proxy_url="socks5://user:pass@127.0.0.1:1080",
            on_banned_callback=MagicMock(),
        ).connect()

        assert haapi_calls[0]["proxy_url"] == "socks5://user:pass@127.0.0.1:1080"
        assert haapi_calls[1]["game_id"] == 1
        assert connection_client_calls[0]["proxy_url"] == (
            "socks5://user:pass@127.0.0.1:1080"
        )
        assert connection_client_calls[1]["game_token"] == "game-token"

    def test_direct_connection_uses_plain_socket(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        plain_socket = MagicMock()
        socks_socket_factory = MagicMock()
        monkeypatch.setattr(
            base_client_module, "socket", MagicMock(return_value=plain_socket)
        )
        monkeypatch.setattr(
            base_client_module.socks, "socksocket", socks_socket_factory
        )

        client = GameClient(bot=runtime_bot, proxy_url=None)

        assert client.client_socket is plain_socket
        socks_socket_factory.assert_not_called()

    def test_connect_socket_does_not_bind_interface(self, runtime_bot: Bot) -> None:
        client = GameClient(bot=runtime_bot, proxy_url="socks5://127.0.0.1:1080")
        client.client_socket = MagicMock()

        client.connect_socket("example.invalid", 5555)

        client.client_socket.bind.assert_not_called()
        client.client_socket.connect.assert_called_once_with(("example.invalid", 5555))

    def test_close_logs_proxy(self, runtime_bot: Bot) -> None:
        client = GameClient(bot=runtime_bot, proxy_url="socks5://127.0.0.1:1080")
        client.client_socket = MagicMock()

        client.close()

        client.client_socket.close.assert_called_once_with()
