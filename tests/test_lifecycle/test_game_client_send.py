from collections import defaultdict
from collections.abc import Callable
from datetime import datetime
from threading import Event, Lock
from typing import cast
from unittest.mock import MagicMock

import pytest
from DBDofusUnity.datas.protos.non_obf.connection.login_message_pb2 import (
    IdentificationResponse,
    LoginMessage,
    Request,
    SelectServerRequest,
    SelectServerResponse,
)
from DBDofusUnity.datas.protos.non_obf.game.connection_pb2 import (
    AuthenticationTicketAcceptedEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.connection_pb2 import (
    IdentificationRequest as GameIdentificationRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.game_action_pb2 import GameActionFightCastRequest
from DBDofusUnity.datas.protos.non_obf.game.spell_pb2 import SpellsEvent
from google.protobuf.message import Message
from DBDofusUnity.dofus_unity_reader.game_constants.server import ServerEnum
from requests import HTTPError
from ankama_launcher_emulator.interfaces.schedule_profile import (
    PersistedProxy,
    ScheduleProfile,
)

from src.core.behaviors.socket import connection_behavior as connection_behavior_module
from src.core.behaviors.behavior import BehaviorState
from src.core.behaviors.socket.connection_behavior import ConnectionBehavior, ConnectionErrorCode
from src.core.bot.bot import Bot
from src.core.bot.bot_manager import BotManager
from src.core.bot.lifecycle import connection_handler as connection_handler_module
from src.core.bot.lifecycle.scheduler import BotScheduler
from src.core.bot import bot_manager as bot_manager_module
from src.core.socket_network import base_client as base_client_module
from src.core.socket_network import connection_client as connection_client_module
from src.core.socket_network import game_client as game_client_module
from src.core.socket_network import socket_client as socket_client_module
from src.core.socket_network.game_client import GameClient
from src.core.socket_network.connection_client import ConnectionClient
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

    monkeypatch.setattr(game_client_module, "get_obf_game_message_from_msg", _fake_obf)
    monkeypatch.setattr(game_client_module, "encode_msg", _fake_encode)
    return client


class TestGameClientSendRoutesToProcessMsg:
    def test_outgoing_cast_request_records_cast_tracking(
        self, game_client: GameClient, runtime_bot: Bot
    ) -> None:
        runtime_bot.game_state.fight.fight_turn = 5
        runtime_bot.debug_recorder = MagicMock()

        clear_msg = GameActionFightCastRequest(spell_id=13052, cell=42)
        game_client.send_msg(clear_msg)

        fight = runtime_bot.game_state.fight
        assert fight.cast_turn_by_spell_id.get(13052) == 5
        assert fight.count_casted_by_spell_id_on_current_turn.get(13052) == 1
        runtime_bot.debug_recorder.record_game_message.assert_called_once()
        recorded_clear_msg = runtime_bot.debug_recorder.record_game_message.call_args.args[0]
        recorded_from_server = runtime_bot.debug_recorder.record_game_message.call_args.args[3]
        assert recorded_clear_msg is clear_msg
        assert recorded_from_server is False
        recorded_source = runtime_bot.debug_recorder.record_game_message.call_args.args[4]
        assert recorded_source == "framework_injected"

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

        def fake_get_game_msg(*args: object, **kwargs: object) -> tuple[None, SpellsEvent, Message, int]:
            return None, clear_msg, obf_msg, 42
        get_game_msg = MagicMock(side_effect=fake_get_game_msg)

        monkeypatch.setattr(game_client_module, "decode_varint_size", fake_decode_varint_size)
        monkeypatch.setattr(game_client_module.config, "DEBUG", True)
        monkeypatch.setattr(
            game_client_module,
            "get_game_msg",
            get_game_msg,
        )

        game_client.on_received_msg_datas(b"\x03abc")

        get_game_msg.assert_called_once_with(b"abc", True, from_server=True)
        runtime_bot.debug_recorder.record_game_message.assert_called_once_with(
            clear_msg, obf_msg, 42, True, "server"
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

        authentication_listener_call = next(
            listener_call
            for listener_call in event_manager_on.call_args_list
            if listener_call.args[0] is AuthenticationTicketAcceptedEvent
        )
        listener_args = authentication_listener_call.args
        listener_kwargs = cast(dict[str, object], authentication_listener_call.kwargs)
        assert listener_args[0] is AuthenticationTicketAcceptedEvent
        assert listener_kwargs["timeout"] == 15.0
        on_timeout = listener_kwargs["on_timeout"]
        assert callable(on_timeout)

        cast(Callable[[], None], on_timeout)()

        request_disconnect.assert_called_once_with()
        sent_message = event_manager_send.call_args.args[0]
        assert isinstance(sent_message, GameIdentificationRequest)


class TestSocketProxyConnection:
    def test_ban_quarantines_proxy_and_preserves_bot_data(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        manager = BotManager.__new__(BotManager)
        lifecycle_events: list[str] = []
        bot_config = MagicMock(schedule_profile="profile-a")
        schedule_profile = ScheduleProfile(
            name_fr="Profile A",
            proxy_id="proxy-a",
            slots_by_day={},
        )

        def record_rejection(proxy_id: str) -> None:
            del proxy_id
            lifecycle_events.append("quarantine")

        monkeypatch.setattr(
            bot_manager_module.BotConfigService,
            "get_bot_config",
            MagicMock(return_value=bot_config),
        )
        monkeypatch.setattr(
            bot_manager_module.ScheduleProfileController,
            "get_profile",
            MagicMock(return_value=schedule_profile),
        )
        monkeypatch.setattr(
            bot_manager_module.ProxyController,
            "record_rejection",
            MagicMock(side_effect=record_rejection),
        )
        quarantine_account = MagicMock()
        monkeypatch.setattr(bot_manager_module.BotStorageController, "quarantine", quarantine_account)

        manager.on_banned_callback("banned@example.com")

        assert lifecycle_events == ["quarantine"]
        quarantine_account.assert_called_once_with("banned@example.com", "Banned account")

    def test_ban_after_profile_reassignment_quarantines_original_proxy(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        manager = BotManager.__new__(BotManager)
        bot_config = MagicMock(schedule_profile="profile-b")
        original_profile = ScheduleProfile(
            name_fr="Profile A",
            proxy_id="proxy-a",
            slots_by_day={},
        )
        monkeypatch.setattr(
            bot_manager_module.BotConfigService,
            "get_bot_config",
            MagicMock(return_value=bot_config),
        )
        monkeypatch.setattr(
            bot_manager_module.BotStorageController,
            "get_all_records",
            MagicMock(
                return_value={
                    "banned@example.com": MagicMock(quarantined_schedule_profile="profile-a")
                }
            ),
        )
        get_profile = MagicMock(return_value=original_profile)
        monkeypatch.setattr(bot_manager_module.ScheduleProfileController, "get_profile", get_profile)
        record_rejection = MagicMock()
        monkeypatch.setattr(bot_manager_module.ProxyController, "record_rejection", record_rejection)
        monkeypatch.setattr(bot_manager_module.BotStorageController, "quarantine", MagicMock())

        manager.on_banned_callback("banned@example.com")

        get_profile.assert_called_once_with("profile-a")
        record_rejection.assert_called_once_with("proxy-a")

    def test_relaunch_reassigns_quarantined_proxy_before_starting_runtime(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        manager = BotManager.__new__(BotManager)
        manager.bot_by_account_id = {0: runtime_bot}
        manager._is_lauching_by_login = defaultdict(Event)
        runtime_bot.is_playing_event.set()
        kill_process = MagicMock()
        monkeypatch.setattr(runtime_bot.process_manager, "kill_process", kill_process)
        bot_config = MagicMock(connection_mode="socket", schedule_profile="profile-a")
        reassigned_config = MagicMock(connection_mode="socket", schedule_profile="profile-b")
        monkeypatch.setattr(
            bot_manager_module.BotConfigService,
            "get_bot_config",
            MagicMock(side_effect=[bot_config, reassigned_config]),
        )
        rejected_proxy = PersistedProxy(
            host="127.0.0.1",
            http_port=8080,
            socks_port=1080,
            username="user",
            password="password",
            rejected=True,
        )
        healthy_proxy = rejected_proxy.model_copy(update={"rejected": False})
        monkeypatch.setattr(
            bot_manager_module.BotConfigService,
            "resolve_bot_proxy",
            MagicMock(side_effect=[rejected_proxy, healthy_proxy]),
        )
        profiles = {
            "profile-a": ScheduleProfile(name_fr="A", proxy_id="a", slots_by_day={}),
            "profile-b": ScheduleProfile(name_fr="B", proxy_id="b", slots_by_day={}),
        }
        monkeypatch.setattr(
            bot_manager_module.ScheduleProfileController,
            "get_all_profiles",
            MagicMock(return_value=profiles),
        )
        monkeypatch.setattr(
            bot_manager_module.ProxyController,
            "get_proxy",
            MagicMock(side_effect=[healthy_proxy]),
        )
        monkeypatch.setattr(
            bot_manager_module.BotStorageController,
            "get_all_records",
            MagicMock(return_value={runtime_bot.account.apikey.login: MagicMock(schedule_profile="profile-a")}),
        )
        reassign = MagicMock()
        monkeypatch.setattr(
            bot_manager_module.BotStorageController,
            "reassign_quarantined_schedule_profile",
            reassign,
        )
        monkeypatch.setattr(runtime_bot, "bot_should_not_play", MagicMock(return_value=False))
        monkeypatch.setattr(manager, "_disconnect_stale_socket_runtime", MagicMock())
        monkeypatch.setattr(manager, "_get_socks_proxy_url", MagicMock(return_value=None))
        monkeypatch.setattr(manager, "_wait_launch_slot", MagicMock())
        socket_client = MagicMock()
        monkeypatch.setattr(bot_manager_module, "SocketClient", socket_client)

        manager.relaunch_account(runtime_bot.account.apikey.login)

        reassign.assert_called_once_with(runtime_bot.account.apikey.login, "profile-b")
        kill_process.assert_called_once_with()
        socket_client.assert_called_once()

    def test_relaunch_rechecks_proxy_quarantine_after_waiting_for_launch_slot(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        manager = BotManager.__new__(BotManager)
        manager.bot_by_account_id = {0: runtime_bot}
        manager._is_lauching_by_login = defaultdict(Event)
        runtime_bot.is_playing_event.set()
        monkeypatch.setattr(runtime_bot.process_manager, "kill_process", MagicMock())
        monkeypatch.setattr(runtime_bot, "bot_should_not_play", MagicMock(return_value=False))
        bot_config = MagicMock(connection_mode="socket", schedule_profile="profile-a")
        reassigned_config = MagicMock(connection_mode="socket", schedule_profile="profile-b")
        monkeypatch.setattr(
            bot_manager_module.BotConfigService,
            "get_bot_config",
            MagicMock(side_effect=[bot_config, reassigned_config]),
        )
        healthy_proxy = PersistedProxy(
            host="127.0.0.1",
            http_port=8080,
            socks_port=1080,
            username="user",
            password="password",
        )
        rejected_proxy = healthy_proxy.model_copy(update={"rejected": True})
        monkeypatch.setattr(
            bot_manager_module.BotConfigService,
            "resolve_bot_proxy",
            MagicMock(side_effect=[healthy_proxy, rejected_proxy]),
        )
        profiles = {
            "profile-a": ScheduleProfile(name_fr="A", proxy_id="a", slots_by_day={}),
            "profile-b": ScheduleProfile(name_fr="B", proxy_id="b", slots_by_day={}),
        }
        monkeypatch.setattr(
            bot_manager_module.ScheduleProfileController,
            "get_all_profiles",
            MagicMock(return_value=profiles),
        )
        monkeypatch.setattr(
            bot_manager_module.ProxyController,
            "get_proxy",
            MagicMock(return_value=healthy_proxy),
        )
        monkeypatch.setattr(
            bot_manager_module.BotStorageController,
            "get_all_records",
            MagicMock(return_value={runtime_bot.account.apikey.login: MagicMock(schedule_profile="profile-a")}),
        )
        reassign = MagicMock()
        monkeypatch.setattr(
            bot_manager_module.BotStorageController,
            "reassign_quarantined_schedule_profile",
            reassign,
        )
        monkeypatch.setattr(manager, "_disconnect_stale_socket_runtime", MagicMock())
        monkeypatch.setattr(manager, "_get_socks_proxy_url", MagicMock(return_value=None))
        monkeypatch.setattr(manager, "_wait_launch_slot", MagicMock())
        socket_client = MagicMock()
        monkeypatch.setattr(bot_manager_module, "SocketClient", socket_client)

        manager.relaunch_account(runtime_bot.account.apikey.login)

        reassign.assert_called_once_with(runtime_bot.account.apikey.login, "profile-b")
        socket_client.assert_called_once()

    def test_outgoing_connection_request_reaches_server_frame(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        connection_behavior = MagicMock()
        connection_client = ConnectionClient(
            bot=runtime_bot,
            connection_behavior=connection_behavior,
            proxy_url=None,
        )
        connection_client.client_socket = MagicMock()
        monkeypatch.setattr(connection_client_module, "encode_msg", _fake_encode)
        request = LoginMessage(
            request=Request(
                uuid="1",
                selectServer=SelectServerRequest(server=ServerEnum.BRIAL),
            )
        )

        connection_client.send_msg(request)

        connection_client.client_socket.sendall.assert_called_once_with(b"")
        assert runtime_bot.game_state.player.server_id == ServerEnum.BRIAL

    def test_scheduled_stop_closes_connected_runtime_when_not_playing(
        self,
        bot_scheduler: BotScheduler,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        request_disconnect = MagicMock()
        is_bot_process_running = MagicMock(return_value=False)
        stop_behaviors = MagicMock()
        bot_scheduler.event_manager.request_disconnect_callback = request_disconnect
        monkeypatch.setattr(
            bot_scheduler.process_manager,
            "is_bot_process_running",
            is_bot_process_running,
        )
        monkeypatch.setattr(
            bot_scheduler.behavior_coordinator,
            "stop_behaviors",
            stop_behaviors,
        )

        bot_scheduler.stop_scheduled_runtime()

        request_disconnect.assert_called_once_with()
        stop_behaviors.assert_called_once_with()

    def test_connection_client_owns_disconnect_callback_during_authentication(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        connection_behavior = MagicMock()
        connection_behavior.state = BehaviorState.RUNNING
        connection_client = ConnectionClient(
            bot=runtime_bot,
            connection_behavior=connection_behavior,
            proxy_url=None,
        )
        connection_client.client_socket = MagicMock()
        monkeypatch.setattr(connection_client, "connect_socket", MagicMock())
        monkeypatch.setattr(
            "src.core.socket_network.connection_client.threading.Thread",
            MagicMock(),
        )

        connection_client.connect("game-token", MagicMock())

        assert runtime_bot.event_manager.request_disconnect_callback == (connection_client.close)
        assert runtime_bot.event_manager.is_socket_mode is True

        connection_client.close()

        assert runtime_bot.event_manager.request_disconnect_callback is None
        assert runtime_bot.event_manager.is_socket_mode is False
        connection_behavior.stop.assert_called_once_with()

    def test_socket_relaunch_closes_previous_runtime_before_connecting(
        self,
        runtime_bot: Bot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        lifecycle_events: list[str] = []
        reconnect_timer = MagicMock()

        def close_previous_runtime() -> None:
            lifecycle_events.append("close")
            runtime_bot.connection_handler.on_disconnected()

        class FakeSocketClient:
            def __init__(self, *args: object, **kwargs: object) -> None:
                del args, kwargs

            def connect(self) -> None:
                lifecycle_events.append("connect")

        manager = BotManager.__new__(BotManager)
        manager.bot_by_account_id = {0: runtime_bot}
        manager._is_lauching_by_login = defaultdict(Event)
        manager._launch_lock = Lock()
        manager._last_launch_time = 0.0
        runtime_bot.is_playing_event.set()
        runtime_bot.is_connected_event.set()
        runtime_bot.event_manager.request_disconnect_callback = close_previous_runtime

        def bot_should_not_play(_current_time: datetime) -> bool:
            return False

        monkeypatch.setattr(runtime_bot, "bot_should_not_play", bot_should_not_play)
        monkeypatch.setattr(manager, "_wait_launch_slot", lambda: None)
        monkeypatch.setattr(connection_handler_module, "Timer", reconnect_timer)
        bot_config = MagicMock(connection_mode="socket", schedule_profile=None)
        monkeypatch.setattr(
            bot_manager_module.BotConfigService,
            "get_bot_config",
            MagicMock(return_value=bot_config),
        )
        monkeypatch.setattr(bot_manager_module, "SocketClient", FakeSocketClient)

        manager.relaunch_account(runtime_bot.account.apikey.login)

        assert lifecycle_events == ["close", "connect"]
        assert runtime_bot.is_playing_event.is_set()
        reconnect_timer.assert_not_called()

        runtime_bot.is_connected_event.set()
        runtime_bot.connection_handler.on_disconnected()

        reconnect_timer.assert_called_once()

    def test_disconnect_clears_connection_scoped_runtime_state(self, runtime_bot: Bot) -> None:
        runtime_bot.game_state.player.character_id = 123
        runtime_bot.game_state.player.character_name = "Renaissance"
        runtime_bot.game_state.map.map_id = 88090898
        runtime_bot.game_state.map.is_in_map_transition = True
        runtime_bot.game_state.fight.in_fight = True
        runtime_bot.game_state.fight.fight_turn = 7
        runtime_bot.game_state.entity.set_actor(make_actor(actor_id=123, cell_id=245))

        runtime_bot.connection_handler.on_disconnected()

        assert runtime_bot.game_state.map.map_id == 88090898
        assert runtime_bot.game_state.map.is_in_map_transition is False
        assert runtime_bot.game_state.fight.in_fight is False
        assert runtime_bot.game_state.fight.fight_turn == 0
        assert runtime_bot.game_state.entity.actor_by_id == {}
        assert runtime_bot.game_state.player.character_id == 123
        assert runtime_bot.game_state.player.character_name == "Renaissance"

    def test_server_selection_success_resets_runtime_capture_sequence(
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
            success=IdentificationResponse.Success(subscription_end_date="2030-01-01T00:00:00")
        )

        monkeypatch.setattr(connection_behavior_module, "RuntimeDataStore", runtime_store_factory)
        monkeypatch.setattr(
            connection_behavior_module,
            "SubscriptionExpirationStorage",
            subscription_storage_factory,
        )

        connection_behavior.on_identification_response(response)

        runtime_store.start_connection_capture_sequence.assert_not_called()
        subscription_storage.record_expiration.assert_called_once()

        connection_behavior.on_select_server_response(
            SelectServerResponse(
                success=SelectServerResponse.Success(
                    token="game-ticket",
                    host="127.0.0.1",
                    ports=[5555],
                )
            )
        )

        runtime_store.start_connection_capture_sequence.assert_called_once_with()

    def test_identification_reason_14_is_treated_as_banned(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        connection_behavior = ConnectionBehavior(
            _logger=MagicMock(),
            event_manager=runtime_bot.event_manager,
            game_state=runtime_bot.game_state,
        )
        finish = MagicMock()
        monkeypatch.setattr(connection_behavior, "finish", finish)

        response = IdentificationResponse(error=IdentificationResponse.Error())
        response.error.reason = cast(IdentificationResponse.Error.Reason, 14)

        connection_behavior.on_identification_response(response)

        finish.assert_called_once_with(ConnectionErrorCode.BANNED, None)

    def test_banned_identification_reason_stays_destructive(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        connection_behavior = ConnectionBehavior(
            _logger=MagicMock(),
            event_manager=runtime_bot.event_manager,
            game_state=runtime_bot.game_state,
        )
        finish = MagicMock()
        monkeypatch.setattr(connection_behavior, "finish", finish)

        connection_behavior.on_identification_response(
            IdentificationResponse(
                error=IdentificationResponse.Error(
                    reason=IdentificationResponse.Error.Reason.BANNED
                )
            )
        )

        finish.assert_called_once_with(ConnectionErrorCode.BANNED, None)

    def test_socket_runtime_uses_socks_proxy_for_token_and_connection(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        haapi_calls: list[dict[str, object]] = []
        connection_client_calls: list[dict[str, object]] = []

        class FakeHaapi:
            def __init__(self, api_key: str, login: str, proxy_url: str | None = None) -> None:
                haapi_calls.append({"api_key": api_key, "login": login, "proxy_url": proxy_url})

            def createToken(self, game_id: int, certificate: object) -> str:
                haapi_calls.append({"game_id": game_id, "certificate": certificate is not None})
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
                connection_client_calls.append({"game_token": game_token, "callback": callback})

        monkeypatch.setattr(socket_client_module, "Haapi", FakeHaapi)
        monkeypatch.setattr(socket_client_module, "ConnectionClient", FakeConnectionClient)

        SocketClient(
            bot=runtime_bot,
            bot_config=MagicMock(),
            socks_proxy_url="socks5://user:pass@127.0.0.1:1080",
            on_banned_callback=MagicMock(),
            on_invalid_auth_callback=MagicMock(),
        ).connect()

        assert haapi_calls[0]["proxy_url"] == "socks5://user:pass@127.0.0.1:1080"
        assert haapi_calls[1]["game_id"] == 1
        assert connection_client_calls[0]["proxy_url"] == ("socks5://user:pass@127.0.0.1:1080")
        assert connection_client_calls[1]["game_token"] == "game-token"

    def test_socket_runtime_resets_stored_auth_on_create_token_auth_failure(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        connection_client = MagicMock()
        invalid_auth_callback = MagicMock()

        class FakeHaapi:
            def __init__(self, api_key: str, login: str, proxy_url: str | None = None) -> None:
                assert proxy_url == "socks5://user:pass@127.0.0.1:1080"

            def createToken(self, game_id: int, certificate: object) -> str:
                raise HTTPError(
                    "HTTP Error: 403 Client Error: Forbidden for url: "
                    "https://haapi.ankama.com/json/Ankama/v5/Account/CreateToken "
                    '- Response: {"status":403,"message":"Unauthorized '
                    "service '\\Ankama\\Account'\"}"
                )

        monkeypatch.setattr(socket_client_module, "Haapi", FakeHaapi)
        monkeypatch.setattr(socket_client_module, "ConnectionClient", connection_client)

        SocketClient(
            bot=runtime_bot,
            bot_config=MagicMock(),
            socks_proxy_url="socks5://user:pass@127.0.0.1:1080",
            on_banned_callback=MagicMock(),
            on_invalid_auth_callback=invalid_auth_callback,
        ).connect()

        invalid_auth_callback.assert_called_once_with(runtime_bot.account.apikey.login)
        connection_client.assert_not_called()

    def test_socket_runtime_confirms_profile_reassignment_after_server_handoff(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        game_client = MagicMock()
        monkeypatch.setattr(socket_client_module, "GameClient", game_client)
        profile_confirmed = MagicMock()
        client = SocketClient(
            bot=runtime_bot,
            bot_config=MagicMock(),
            socks_proxy_url="socks5://user:pass@127.0.0.1:1080",
            on_banned_callback=MagicMock(),
            on_invalid_auth_callback=MagicMock(),
            on_connection_server_succeeded=profile_confirmed,
        )
        client._connection_client = MagicMock()

        client.connected_server(
            None,
            MagicMock(host="game.example", port=5555, ticket="game-ticket"),
        )

        profile_confirmed.assert_called_once_with(runtime_bot.account.apikey.login)

    def test_direct_connection_uses_plain_socket(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        plain_socket = MagicMock()
        socks_socket_factory = MagicMock()
        monkeypatch.setattr(base_client_module, "socket", MagicMock(return_value=plain_socket))
        monkeypatch.setattr(base_client_module.socks, "socksocket", socks_socket_factory)

        client = GameClient(bot=runtime_bot, proxy_url=None)

        assert client.client_socket is plain_socket
        socks_socket_factory.assert_not_called()

    def test_connect_socket_does_not_bind_interface(self, runtime_bot: Bot) -> None:
        client = GameClient(bot=runtime_bot, proxy_url="socks5://127.0.0.1:1080")
        client.client_socket = MagicMock()

        client.connect_socket("example.invalid", 5555)

        client.client_socket.bind.assert_not_called()
        client.client_socket.connect.assert_called_once_with(("example.invalid", 5555))

    def test_fragmented_varint_header_waits_for_next_read(
        self, game_client: GameClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        received_message = MagicMock()
        monkeypatch.setattr(game_client, "on_received_msg_datas", received_message)
        payload = b"x" * 128

        game_client.handle(b"\x80")

        received_message.assert_not_called()
        assert game_client.buffer == b"\x80"

        game_client.handle(b"\x01" + payload)

        received_message.assert_called_once_with(b"\x80\x01" + payload)
        assert game_client.buffer == b""

    def test_close_cancels_frame_timers(self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch) -> None:
        client = GameClient(bot=runtime_bot, proxy_url="socks5://127.0.0.1:1080")
        client.client_socket = MagicMock()
        cancel_frame_timers = MagicMock()
        monkeypatch.setattr(runtime_bot, "cancel_frame_timers", cancel_frame_timers)

        client.close()
        client.close()

        cancel_frame_timers.assert_called_once_with()
        client.client_socket.close.assert_called_once_with()
