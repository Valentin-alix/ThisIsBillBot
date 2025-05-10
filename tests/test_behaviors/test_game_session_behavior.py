from collections.abc import Callable
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from datas.protos.non_obf.game.basic_pb2 import (
    BasicLatencyStatsEvent,
    BasicLatencyStatsRequest,
)
from connection_pb2 import PongEvent
from datas.protos.non_obf.game.fight_pb2 import (
    FightIsTurnReadyEvent,
    FightTurnFinishRequest,
    FightTurnReadyRequest,
)
from datas.protos.non_obf.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    SequenceEndEvent,
    SequenceStartEvent,
)
from google.protobuf.message import Message
from pytest import MonkeyPatch
import pytest

from src.core.behaviors.socket.game_session_behavior import GameSessionBehavior
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext, set_game_state

PLAYER_ID = 71808188767
ENEMY_ID = -1


def _run_timer_immediately(
    behavior: GameSessionBehavior,
    range_time: tuple[float, float] | float,
    func: Callable[[], None],
) -> None:
    del behavior, range_time
    func()


def _make_running_game_session_behavior(
    game_state_ctx: GameStateContext,
    monkeypatch: MonkeyPatch,
    *,
    player_id: int = PLAYER_ID,
) -> tuple[EventManager, list[Message]]:
    monkeypatch.setattr(GameSessionBehavior, "run_timer", _run_timer_immediately)
    game_state_ctx.game_state.player.character_id = player_id
    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append
    behavior = GameSessionBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
    )
    behavior.start(callback=None, parent=None)
    return event_manager, sent_messages


class TestGameSessionBehavior:
    def test_sends_turn_ready_for_enemy_ready_event(
        self,
        game_state_ctx: GameStateContext,
        monkeypatch: MonkeyPatch,
    ) -> None:
        event_manager, sent_messages = _make_running_game_session_behavior(
            game_state_ctx, monkeypatch
        )

        event_manager.process_msg(FightIsTurnReadyEvent(character_id=ENEMY_ID))

        assert [type(sent_message) for sent_message in sent_messages] == [
            FightTurnReadyRequest
        ]

    def test_final_fight_turn_finish_sends_turn_ready(
        self,
        game_state_ctx: GameStateContext,
        monkeypatch: MonkeyPatch,
    ) -> None:
        set_game_state(
            game_state_ctx.game_state,
            player_cell_id=344,
            enemy_cell_ids=[],
        )
        event_manager, sent_messages = _make_running_game_session_behavior(
            game_state_ctx,
            monkeypatch,
            player_id=game_state_ctx.game_state.player.character_id,
        )

        event_manager.process_msg(FightTurnFinishRequest())

        assert [type(sent_message) for sent_message in sent_messages] == [
            FightTurnReadyRequest
        ]

    def test_non_final_fight_turn_finish_does_not_send_turn_ready(
        self,
        game_state_ctx: GameStateContext,
        monkeypatch: MonkeyPatch,
    ) -> None:
        set_game_state(
            game_state_ctx.game_state,
            player_cell_id=344,
            enemy_cell_ids=[358],
        )
        event_manager, sent_messages = _make_running_game_session_behavior(
            game_state_ctx,
            monkeypatch,
            player_id=game_state_ctx.game_state.player.character_id,
        )

        event_manager.process_msg(FightTurnFinishRequest())

        assert sent_messages == []

    def test_pending_enemy_turn_ready_flushes_after_enemy_sequence_without_ack(
        self,
        game_state_ctx: GameStateContext,
        monkeypatch: MonkeyPatch,
    ) -> None:
        event_manager, sent_messages = _make_running_game_session_behavior(
            game_state_ctx, monkeypatch
        )

        event_manager.process_msg(SequenceStartEvent(author_id=ENEMY_ID))
        event_manager.process_msg(FightIsTurnReadyEvent(character_id=ENEMY_ID))
        event_manager.process_msg(SequenceEndEvent(author_id=ENEMY_ID, action_id=3))

        assert [type(sent_message) for sent_message in sent_messages] == [
            FightTurnReadyRequest
        ]
        assert not any(
            isinstance(sent_message, GameActionAcknowledgementRequest)
            for sent_message in sent_messages
        )

    def test_player_sequence_end_still_sends_ack(
        self,
        game_state_ctx: GameStateContext,
        monkeypatch: MonkeyPatch,
    ) -> None:
        event_manager, sent_messages = _make_running_game_session_behavior(
            game_state_ctx, monkeypatch
        )

        event_manager.process_msg(SequenceStartEvent(author_id=PLAYER_ID))
        event_manager.process_msg(SequenceEndEvent(author_id=PLAYER_ID, action_id=59))

        assert [type(sent_message) for sent_message in sent_messages] == [
            GameActionAcknowledgementRequest
        ]
        ack = sent_messages[0]
        assert isinstance(ack, GameActionAcknowledgementRequest)
        assert ack.valid is True
        assert ack.action_id == 59

    def test_basic_latency_before_first_pong_sends_initial_latency(
        self,
        game_state_ctx: GameStateContext,
    ) -> None:
        event_manager = EventManager(_logger=game_state_ctx.logger)
        sent_messages: list[Message] = []
        event_manager.on_send_game_callback = sent_messages.append
        behavior = GameSessionBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            _logger=game_state_ctx.logger,
        )
        logger = MagicMock()
        behavior.logger = logger

        with pytest.raises(AssertionError):
            behavior._on_basic_latency(BasicLatencyStatsEvent())

        assert sent_messages == []
        logger.error.assert_called_once_with(
            "BasicLatencyStatsEvent received before latency was measured: "
            "sent_datetime_ping_request=None"
        )

    def test_basic_latency_sends_measured_latency(
        self,
        game_state_ctx: GameStateContext,
        monkeypatch: MonkeyPatch,
    ) -> None:
        event_manager, sent_messages = _make_running_game_session_behavior(
            game_state_ctx, monkeypatch
        )
        game_state_ctx.game_state.server.latency = 42

        event_manager.process_msg(BasicLatencyStatsEvent())

        assert [type(sent_message) for sent_message in sent_messages] == [
            BasicLatencyStatsRequest
        ]
        latency_request = sent_messages[0]
        assert isinstance(latency_request, BasicLatencyStatsRequest)
        assert latency_request.latency == 42

    def test_pong_updates_measured_latency_and_clears_pending_ping(
        self,
        game_state_ctx: GameStateContext,
        monkeypatch: MonkeyPatch,
    ) -> None:
        event_manager, sent_messages = _make_running_game_session_behavior(
            game_state_ctx, monkeypatch
        )
        del sent_messages
        game_state_ctx.game_state.server.sent_datetime_ping_request = (
            datetime.now() - timedelta(milliseconds=25)
        )

        event_manager.process_msg(PongEvent())

        latency = game_state_ctx.game_state.server.latency
        assert latency is not None
        assert latency >= 0
        assert game_state_ctx.game_state.server.sent_datetime_ping_request is None

    def test_pong_without_pending_ping_logs_before_error(
        self,
        game_state_ctx: GameStateContext,
    ) -> None:
        event_manager = EventManager(_logger=game_state_ctx.logger)
        behavior = GameSessionBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            _logger=game_state_ctx.logger,
        )
        logger = MagicMock()
        behavior.logger = logger

        with pytest.raises(ValueError):
            behavior.on_pong_event(PongEvent())

        logger.error.assert_called_once_with(
            "PongEvent received without pending PingRequest"
        )

    def test_sequence_end_without_sequence_start_logs_warning(
        self,
        game_state_ctx: GameStateContext,
    ) -> None:
        event_manager = EventManager(_logger=game_state_ctx.logger)
        event_manager.on_send_game_callback = lambda sent_message: None
        behavior = GameSessionBehavior(
            event_manager=event_manager,
            game_state=game_state_ctx.game_state,
            _logger=game_state_ctx.logger,
        )
        logger = MagicMock()
        behavior.logger = logger

        behavior._on_sequence_end(SequenceEndEvent(author_id=ENEMY_ID, action_id=3))

        logger.warning.assert_called_once_with(
            "SequenceEndEvent received without matching SequenceStartEvent: "
            "author_id=-1, action_id=3"
        )
