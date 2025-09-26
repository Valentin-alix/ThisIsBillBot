from unittest.mock import MagicMock

from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveRequest
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeAcceptRequest,
    ExchangeRequestedTradeEvent,
)
from google.protobuf.message import Message
from pytest import MonkeyPatch

from src.core.behaviors.storage.mule.mule_accept_behavior import MuleAcceptBehavior
from src.core.bot.kamas_mule_registry import KamasMuleRegistry
from src.core.events_manager.event_manager import EventManager
from src.services.human_timings import HumanTimingsService
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext


def setup_function() -> None:
    KamasMuleRegistry().clear()


def teardown_function() -> None:
    KamasMuleRegistry().clear()


def _get_fixed_base_action_timing(service: HumanTimingsService) -> float:
    del service
    return 1.0


def test_unreserved_request_does_not_hide_reserved_donor_request(
    game_state_ctx: GameStateContext,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(HumanTimingsService, "get_timing_base_action", _get_fixed_base_action_timing)
    registry = KamasMuleRegistry()
    game_state_ctx.game_state.player.character_id = 100
    game_state_ctx.game_state.map.map_id = 200

    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    delayed_messages: list[tuple[Message, tuple[float, float] | float]] = []
    event_manager.on_send_game_callback = sent_messages.append
    behavior = MuleAcceptBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        auto_trip_smart_behavior=MagicMock(),
        unload_behavior=MagicMock(),
        sale_hotel_prices_behavior=MagicMock(),
        mule_registry=registry,
        _logger=game_state_ctx.logger,
    )

    def capture_delayed_message(message: Message, delay: tuple[float, float] | float) -> None:
        delayed_messages.append((message, delay))

    behavior.send_message_delayed = capture_delayed_message
    behavior.stand_ready_for_exchanges()
    reservation = registry.reserve(
        game_state_ctx.game_state.player.server_id,
        donor_character_id=999,
    )
    assert reservation is not None

    event_manager.process_msg(ExchangeRequestedTradeEvent(source_id=998))

    assert len(event_manager.listeners_by_type_msg[ExchangeRequestedTradeEvent]) == 1
    assert [type(message) for message in sent_messages] == [DialogLeaveRequest]
    assert behavior.timers == []

    event_manager.process_msg(ExchangeRequestedTradeEvent(source_id=999))

    assert event_manager.listeners_by_type_msg[ExchangeRequestedTradeEvent] == []
    assert len(delayed_messages) == 1
    message, delay = delayed_messages[0]
    assert isinstance(message, ExchangeAcceptRequest)
    assert delay == 1.0
