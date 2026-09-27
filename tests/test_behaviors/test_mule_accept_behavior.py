from collections.abc import Callable, Iterator
from datetime import datetime
from threading import Thread
from unittest.mock import MagicMock

import pytest
from DBDofusUnity.datas.protos.non_obf.game.character_pb2 import (
    PlayerStatusUpdatedEvent,
    PlayerStatusUpdateRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import CharacterStatus
from DBDofusUnity.datas.protos.non_obf.game.context_pb2 import ContextCreationEvent

from DBDofusUnity.datas.protos.non_obf.game.dialog_pb2 import DialogLeaveRequest
from DBDofusUnity.datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeAcceptRequest,
    ExchangeLeaveEvent,
    ExchangePlayerRequest,
    ExchangeRequestedTradeEvent,
)
from google.protobuf.message import Message
from pytest import MonkeyPatch

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.storage.mule import mule_give_behavior as mule_give_module
from src.core.behaviors.storage.mule.mule_accept_behavior import MuleAcceptBehavior
from src.core.behaviors.storage.mule.mule_give_behavior import MuleGiveBehavior
from src.core.bot.bot import Bot
from src.core.bot.kamas_mule_registry import KamasMuleRegistry, MuleReservation
from src.core.events_manager.event_manager import EventManager
from src.services.human_timings import HumanTimingsService
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext
from tests.fixtures.entities import make_actor


def setup_function() -> None:
    KamasMuleRegistry().clear()


def teardown_function() -> None:
    KamasMuleRegistry().clear()


def _get_fixed_base_action_timing(service: HumanTimingsService) -> float:
    del service
    return 1.0


@pytest.fixture
def mule(game_state_ctx: GameStateContext) -> Iterator[tuple[MuleAcceptBehavior, list[Message]]]:
    registry = KamasMuleRegistry()
    game_state_ctx.game_state.player.character_id = 100
    game_state_ctx.game_state.map.map_id = 200
    game_state_ctx.game_state.sale_hotel.last_time_updated_prices = datetime.now()

    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append

    def arrive_at_bank(
        *, map_ids: set[int], callback: Callable[[str | None], None], parent: Behavior
    ) -> None:
        callback(None)

    trip = MagicMock()
    trip.start.side_effect = arrive_at_bank
    behavior = MuleAcceptBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        auto_trip_smart_behavior=trip,
        unload_behavior=MagicMock(),
        sale_hotel_prices_behavior=MagicMock(),
        mule_registry=registry,
        _logger=game_state_ctx.logger,
    )

    behavior.start(callback=None, parent=None)
    yield behavior, sent_messages
    behavior.stop()


def test_unreserved_request_does_not_hide_reserved_donor_request(
    mule: tuple[MuleAcceptBehavior, list[Message]],
    game_state_ctx: GameStateContext,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(HumanTimingsService, "get_timing_base_action", _get_fixed_base_action_timing)
    behavior, sent_messages = mule
    event_manager = behavior.event_manager
    registry = behavior.mule_registry
    delayed_messages: list[tuple[Message, tuple[float, float] | float]] = []

    def capture_delayed_message(message: Message, delay: tuple[float, float] | float) -> None:
        delayed_messages.append((message, delay))

    behavior.send_message_delayed = capture_delayed_message
    reservation = registry.reserve(game_state_ctx.game_state.player.server_id, donor_character_id=999)
    assert reservation is not None
    registry.exchange_signals.preparation_requested.emit(reservation.token)
    event_manager.process_msg(
        PlayerStatusUpdatedEvent(
            player_id=100, status=CharacterStatus(status=CharacterStatus.STATUS_AVAILABLE)
        )
    )
    sent_messages.clear()

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


def _prepare(behavior: MuleAcceptBehavior) -> MuleReservation:
    reservation = behavior.mule_registry.reserve(behavior.game_state.player.server_id, 999)
    assert reservation is not None
    behavior.mule_registry.exchange_signals.preparation_requested.emit(reservation.token)
    return reservation


def _confirm_available(behavior: MuleAcceptBehavior, player_id: int = 100) -> None:
    behavior.event_manager.process_msg(
        PlayerStatusUpdatedEvent(
            player_id=player_id, status=CharacterStatus(status=CharacterStatus.STATUS_AVAILABLE)
        )
    )


def test_mule_stays_solo_until_reserved_donor_requests_preparation(
    mule: tuple[MuleAcceptBehavior, list[Message]],
) -> None:
    behavior, sent = mule
    assert sent == []
    reservation = behavior.mule_registry.reserve(behavior.game_state.player.server_id, 999)
    assert reservation is not None
    assert sent == []
    behavior.mule_registry.exchange_signals.preparation_requested.emit("unrelated-token")
    assert sent == []
    behavior.mule_registry.exchange_signals.preparation_requested.emit(reservation.token)
    assert sent == [
        PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_AVAILABLE))
    ]


def test_donor_is_notified_only_after_own_available_confirmation(
    mule: tuple[MuleAcceptBehavior, list[Message]],
) -> None:
    behavior, _ = mule
    prepared = MagicMock()
    behavior.mule_registry.exchange_signals.prepared.connect(prepared)
    try:
        reservation = _prepare(behavior)
        prepared.assert_not_called()
        _confirm_available(behavior, player_id=999)
        prepared.assert_not_called()
        _confirm_available(behavior)
        prepared.assert_called_once_with(reservation.token)
    finally:
        behavior.mule_registry.exchange_signals.prepared.disconnect(prepared)


@pytest.mark.parametrize("end_exchange", [False, True])
def test_mule_returns_to_solo_and_becomes_unavailable(
    mule: tuple[MuleAcceptBehavior, list[Message]],
    end_exchange: bool,
) -> None:
    behavior, sent = mule
    behavior.run_timer = MagicMock()
    _prepare(behavior)
    _confirm_available(behavior)
    if end_exchange:
        behavior.on_exchange_leave_event(ExchangeLeaveEvent())
    else:
        behavior.stop()
    assert sent[-1] == PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_SOLO))
    assert behavior.mule_registry.reserve(behavior.game_state.player.server_id, 999) is None
    behavior.stop()
    assert len(sent) == 2


@pytest.mark.parametrize("confirmed", [False, True])
def test_donor_cancellation_restores_solo_and_ignores_late_confirmation(
    mule: tuple[MuleAcceptBehavior, list[Message]],
    confirmed: bool,
) -> None:
    behavior, sent = mule
    reservation = _prepare(behavior)
    if confirmed:
        _confirm_available(behavior)
    behavior.mule_registry.release(reservation.token)
    _confirm_available(behavior)
    assert sent[-1] == PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_SOLO))
    assert behavior.mule_registry.reserve(behavior.game_state.player.server_id, 998) is not None


def test_disconnected_mule_cleanup_does_not_send_status(
    mule: tuple[MuleAcceptBehavior, list[Message]],
) -> None:
    behavior, sent = mule
    _prepare(behavior)
    behavior.event_manager.on_send_game_callback = None
    behavior.stop()
    assert len(sent) == 1
    assert behavior.mule_registry.reserve(behavior.game_state.player.server_id, 999) is None


@pytest.mark.parametrize("interrupted_by_fight", [False, True])
def test_mule_reconnects_coordination_when_restarted(
    mule: tuple[MuleAcceptBehavior, list[Message]],
    interrupted_by_fight: bool,
) -> None:
    behavior, sent = mule
    reservation = _prepare(behavior)
    if interrupted_by_fight:
        behavior.event_manager.process_msg(
            ContextCreationEvent(context=ContextCreationEvent.GameContext.FIGHT)
        )
    else:
        behavior.stop()
    assert sent[-1] == PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_SOLO))
    sent.clear()
    behavior.mule_registry.exchange_signals.preparation_requested.emit(reservation.token)
    assert sent == []

    if interrupted_by_fight:
        behavior.on_recovered(None)
    else:
        behavior.start(callback=None, parent=None)
    assert sent == []
    _prepare(behavior)
    _confirm_available(behavior)
    assert sent == [
        PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_AVAILABLE))
    ]


@pytest.mark.parametrize("confirm_status", [False, True])
def test_donor_opens_window_only_after_arrival_and_waits_for_confirmation(
    mule: tuple[MuleAcceptBehavior, list[Message]],
    runtime_bot: Bot,
    confirm_status: bool,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(HumanTimingsService, "get_timing_base_action", _get_fixed_base_action_timing)
    receiver, receiver_sent = mule
    runtime_bot.game_state.player.character_id = 999
    runtime_bot.game_state.map.map_id = 200
    runtime_bot.game_state.entity.set_actor(make_actor(actor_id=100, cell_id=120))
    sent: list[Message] = []
    runtime_bot.event_manager.on_send_game_callback = sent.append
    trip = MagicMock()
    donor = MuleGiveBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=runtime_bot.event_manager,
        game_state=runtime_bot.game_state,
        auto_trip_smart_behavior=trip,
        _logger=runtime_bot.logger,
    )
    timer_factory = MagicMock()
    monkeypatch.setattr(mule_give_module, "Timer", timer_factory)
    donor.send_message_delayed = lambda message, delay: sent.append(message)
    donor.start(callback=None, parent=None)
    try:
        trip.start.assert_called_once()
        assert receiver_sent == []
        worker = Thread(target=donor.on_auto_trip_smart_behavior_finished, args=(None,))
        worker.start()
        worker.join(timeout=2)
        assert not worker.is_alive()
        assert receiver_sent == [
            PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_AVAILABLE))
        ]
        assert sent == []
        receiver.mule_registry.exchange_signals.prepared.emit("unrelated-token")
        assert sent == []
        if confirm_status:
            _confirm_available(receiver)
            assert sent == [ExchangePlayerRequest(target_id=100)]
            timer_factory.return_value.cancel.assert_called_once()
        else:
            timeout_callback: Callable[[], None] = timer_factory.call_args.args[1]
            timeout_callback()
            _confirm_available(receiver)
            assert not any(isinstance(message, ExchangePlayerRequest) for message in sent)
    finally:
        donor.stop()
    assert receiver_sent[-1] == PlayerStatusUpdateRequest(
        status=CharacterStatus(status=CharacterStatus.STATUS_SOLO)
    )
