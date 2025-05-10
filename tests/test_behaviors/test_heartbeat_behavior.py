from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from datas.protos.non_obf.game.connection_pb2 import PingRequest
from google.protobuf.message import Message
from pytest import MonkeyPatch

from src.core.behaviors.socket import heartbeat_behavior
from src.core.behaviors.socket.heartbeat_behavior import HearthBeatBehavior
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext


class FakeThread:
    started = False

    def __init__(self, target: Callable[[], None], daemon: bool) -> None:
        self.target = target
        self.daemon = daemon

    def start(self) -> None:
        FakeThread.started = True


def test_heartbeat_sends_ping_immediately_on_start(
    game_state_ctx: GameStateContext,
    monkeypatch: MonkeyPatch,
) -> None:
    FakeThread.started = False
    monkeypatch.setattr(heartbeat_behavior.threading, "Thread", FakeThread)
    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append
    behavior = HearthBeatBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
    )

    behavior.start(callback=None, parent=None)

    assert FakeThread.started is True
    assert [type(sent_message) for sent_message in sent_messages] == [PingRequest]
    assert game_state_ctx.game_state.server.sent_datetime_ping_request is not None


def test_heartbeat_logs_when_previous_ping_is_still_pending(
    game_state_ctx: GameStateContext,
) -> None:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    event_manager.on_send_game_callback = lambda sent_message: None
    behavior = HearthBeatBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
    )
    logger = MagicMock()
    behavior.logger = logger
    game_state_ctx.game_state.server.sent_datetime_ping_request = (
        datetime.now() - timedelta(milliseconds=50)
    )

    behavior._send_ping()

    warning_message = logger.warning.call_args.args[0]
    assert warning_message.startswith(
        "Sending PingRequest while previous ping is still pending: "
    )
