import unittest
from unittest.mock import create_autospec, patch

from src.core.behaviors.behavior import BehaviorState
from src.core.behaviors.socket.connection_behavior import ConnectionBehavior
from src.core.bot.bot import Bot
from src.core.socket_network.connection_client import ConnectionClient
from src.core.socket_network.game_client import GameClient


class DummyLogger:
    def info(self, _message: str) -> None:
        return None

    def warning(self, _message: str) -> None:
        return None

    def error(self, _message: str) -> None:
        return None


class RecordingEventManager:
    def __init__(self, events: list[str], error: Exception | None = None) -> None:
        self._events = events
        self._error = error
        self.sent_messages: list[object] = []

    def process_msg(self, _msg: object) -> None:
        self._events.append("process")
        if self._error is not None:
            raise self._error

    def send(self, msg: object) -> None:
        self.sent_messages.append(msg)

    def clear_listener_by_origin(self, _originator: object) -> None:
        return None


class RecordingMsgInfoSignals:
    def __init__(self, events: list[str]) -> None:
        self.msg_info = self
        self._events = events
        self.emitted: list[tuple[object, bool]] = []

    def emit(self, msg_info: object, was_send_from_proxy: bool) -> None:
        self._events.append("emit")
        self.emitted.append((msg_info, was_send_from_proxy))


class RecordingHandshakeBehavior:
    def __init__(self) -> None:
        self.state = BehaviorState.STOPPED
        self.start_calls: list[dict[str, object | None]] = []
        self.stop_call_count = 0

    def start(
        self, *, ticket: str, callback: object | None, parent: object | None
    ) -> None:
        self.start_calls.append(
            {"ticket": ticket, "callback": callback, "parent": parent}
        )

    def stop(self) -> None:
        self.stop_call_count += 1


class DummyGameInfoSignals:
    def disconnected(self) -> None:
        return None


def make_bot(
    events: list[str], error: Exception | None = None
) -> tuple[
    Bot, RecordingMsgInfoSignals, RecordingEventManager, RecordingHandshakeBehavior
]:
    bot = create_autospec(Bot, instance=True)
    signals = RecordingMsgInfoSignals(events)
    event_manager = RecordingEventManager(events, error=error)
    handshake_behavior = RecordingHandshakeBehavior()
    bot.event_manager = event_manager
    bot.msg_info_signals = signals
    bot.logger = DummyLogger()
    bot.handshake_behavior = handshake_behavior
    bot.game_info_signals = DummyGameInfoSignals()
    return bot, signals, event_manager, handshake_behavior


class SocketClientsTests(unittest.TestCase):
    def test_connection_client_emits_before_processing_received_message(self) -> None:
        events: list[str] = []
        bot, signals, _event_manager, _handshake_behavior = make_bot(events)
        connection_behavior = create_autospec(ConnectionBehavior, instance=True)
        client = ConnectionClient(bot=bot, connection_behavior=connection_behavior)
        self.addCleanup(client.client_socket.close)
        fake_msg = object()
        fake_info = object()

        with (
            patch(
                "src.core.socket_network.connection_client.decode_varint_size",
                return_value=(1, 0),
            ),
            patch(
                "src.core.socket_network.connection_client.get_conn_msg",
                return_value=(object(), fake_msg),
            ),
            patch(
                "src.core.socket_network.connection_client.get_conn_msg_info",
                return_value=fake_info,
            ),
        ):
            client.on_received_msg_datas(b"x")

        self.assertEqual(events, ["emit", "process"])
        self.assertEqual(signals.emitted, [(fake_info, False)])

    def test_connection_client_emits_before_processing_even_if_processing_fails(
        self,
    ) -> None:
        events: list[str] = []
        bot, signals, _event_manager, _handshake_behavior = make_bot(
            events, error=RuntimeError("boom")
        )
        connection_behavior = create_autospec(ConnectionBehavior, instance=True)
        client = ConnectionClient(bot=bot, connection_behavior=connection_behavior)
        self.addCleanup(client.client_socket.close)

        with (
            patch(
                "src.core.socket_network.connection_client.decode_varint_size",
                return_value=(1, 0),
            ),
            patch(
                "src.core.socket_network.connection_client.get_conn_msg",
                return_value=(object(), object()),
            ),
            patch(
                "src.core.socket_network.connection_client.get_conn_msg_info",
                return_value=object(),
            ),
        ):
            with self.assertRaises(RuntimeError):
                client.on_received_msg_datas(b"x")

        self.assertEqual(events, ["emit", "process"])
        self.assertEqual(len(signals.emitted), 1)

    def test_game_client_emits_before_processing_received_message(self) -> None:
        events: list[str] = []
        bot, signals, _event_manager, _handshake_behavior = make_bot(events)
        client = GameClient(bot=bot)
        self.addCleanup(client.client_socket.close)
        clear_msg = object()
        obf_msg = object()
        fake_info = object()

        with (
            patch(
                "src.core.socket_network.game_client.decode_varint_size",
                return_value=(1, 0),
            ),
            patch(
                "src.core.socket_network.game_client.get_game_msg",
                return_value=("root", clear_msg, obf_msg, 12),
            ),
            patch(
                "src.core.socket_network.game_client.get_game_msg_info",
                return_value=fake_info,
            ),
        ):
            client.on_received_msg_datas(b"x")

        self.assertEqual(events, ["emit", "process"])
        self.assertEqual(signals.emitted, [(fake_info, False)])

    def test_game_client_emits_without_processing_when_clear_message_is_missing(
        self,
    ) -> None:
        events: list[str] = []
        bot, signals, _event_manager, _handshake_behavior = make_bot(events)
        client = GameClient(bot=bot)
        self.addCleanup(client.client_socket.close)

        with (
            patch(
                "src.core.socket_network.game_client.decode_varint_size",
                return_value=(1, 0),
            ),
            patch(
                "src.core.socket_network.game_client.get_game_msg",
                return_value=("root", None, object(), 12),
            ),
            patch(
                "src.core.socket_network.game_client.get_game_msg_info",
                return_value=object(),
            ),
        ):
            client.on_received_msg_datas(b"x")

        self.assertEqual(events, ["emit"])
        self.assertEqual(len(signals.emitted), 1)

    def test_game_client_connect_starts_handshake_behavior(self) -> None:
        events: list[str] = []
        bot, _signals, _event_manager, handshake_behavior = make_bot(events)
        connection_behavior = create_autospec(ConnectionBehavior, instance=True)
        bot.connection_behavior = connection_behavior
        client = GameClient(bot=bot)
        self.addCleanup(client.client_socket.close)

        with (
            patch("src.core.socket_network.base_client.socket.connect") as connect_mock,
            patch(
                "src.core.socket_network.game_client.threading.Thread"
            ) as thread_mock,
        ):
            client.connect("127.0.0.1", 5555, "ticket")

        self.assertEqual(connect_mock.call_count, 1)
        self.assertEqual(connect_mock.call_args.args, (("127.0.0.1", 5555),))
        self.assertEqual(
            handshake_behavior.start_calls,
            [{"ticket": "ticket", "callback": None, "parent": None}],
        )
        self.assertEqual(thread_mock.call_count, 1)

    def test_game_client_on_close_stops_running_handshake_behavior(self) -> None:
        events: list[str] = []
        bot, _signals, _event_manager, handshake_behavior = make_bot(events)
        handshake_behavior.state = BehaviorState.RUNNING
        client = GameClient(bot=bot)
        self.addCleanup(client.client_socket.close)

        with patch(
            "src.core.socket_network.game_client.QMetaObject.invokeMethod"
        ) as invoke_method_mock:
            client.on_close()

        self.assertEqual(handshake_behavior.stop_call_count, 1)
        self.assertEqual(invoke_method_mock.call_count, 1)

    def test_game_client_on_close_keeps_stopped_handshake_behavior_untouched(
        self,
    ) -> None:
        events: list[str] = []
        bot, _signals, _event_manager, handshake_behavior = make_bot(events)
        handshake_behavior.state = BehaviorState.STOPPED
        client = GameClient(bot=bot)
        self.addCleanup(client.client_socket.close)

        with patch("src.core.socket_network.game_client.QMetaObject.invokeMethod"):
            client.on_close()

        self.assertEqual(handshake_behavior.stop_call_count, 0)


if __name__ == "__main__":
    unittest.main()
