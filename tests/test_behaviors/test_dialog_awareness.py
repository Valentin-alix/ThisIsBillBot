from collections.abc import Callable
from threading import Event
from unittest.mock import MagicMock

import pytest

from DBDofusUnity.datas.protos.non_obf.game.dialog_pb2 import DialogLeaveEvent, DialogLeaveRequest
from DBDofusUnity.datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeCraftStartedEvent,
    ExchangeLeaveEvent,
    ExchangeRequestedTradeEvent,
    ExchangeStartedWithStorageEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import MapCurrentEvent, MapMovementRequest
from DBDofusUnity.datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent
from DBDofusUnity.datas.protos.non_obf.game.teleportation_pb2 import TeleportDestinationsEvent
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from google.protobuf.message import Message

from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.events_manager.event_manager import EventManager
from src.core.frames.dialog_frame import DialogFrame
from src.core.states.dialog_state import OpenDialogKind
from src.core.states.map_state import MapState
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext

BANK_STORAGE_SLOT = 20_000
SMALL_STORAGE_SLOT = 50
START_CELL_ID = 305
END_CELL_ID = 306
CRAFT_SKILL_ID = 42


def _run_timer_inline(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
    del range_time
    func()


def _make_event_manager(game_state_ctx: GameStateContext) -> tuple[EventManager, list[Message]]:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append
    return event_manager, sent_messages


def _make_dialog_frame(game_state_ctx: GameStateContext) -> EventManager:
    event_manager, _ = _make_event_manager(game_state_ctx)
    DialogFrame(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        game_info_signals=game_state_ctx.game_info_signals,
        inventory_signals=game_state_ctx.inventory_signals,
        is_playing_event=Event(),
        _logger=game_state_ctx.logger,
    )
    return event_manager


def test_opening_the_personal_chest_is_recorded(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(ExchangeStartedWithStorageEvent(storage_max_slot=BANK_STORAGE_SLOT))

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.BANK_STORAGE)


def test_a_small_storage_is_not_the_personal_chest(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(ExchangeStartedWithStorageEvent(storage_max_slot=SMALL_STORAGE_SLOT))

    assert not game_state_ctx.game_state.dialog.is_any_open


def test_a_workshop_is_recorded_with_its_skill(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(ExchangeCraftStartedEvent(skill_id=CRAFT_SKILL_ID))

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.CRAFT, context_id=CRAFT_SKILL_ID)
    assert not game_state_ctx.game_state.dialog.is_open(OpenDialogKind.CRAFT, context_id=CRAFT_SKILL_ID + 1)


def test_a_npc_question_is_recorded(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(NpcDialogQuestionEvent(message_id=1))

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.NPC_DIALOG)


def test_the_zaap_destination_screen_is_recorded(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(TeleportDestinationsEvent())

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.ZAAP_DESTINATIONS)


def test_a_trade_request_from_another_player_is_recorded(
    game_state_ctx: GameStateContext,
) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(ExchangeRequestedTradeEvent(source_id=1, target_id=2))

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.TRADE_REQUEST)


def test_leaving_an_exchange_clears_the_state(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)
    event_manager.process_msg(ExchangeStartedWithStorageEvent(storage_max_slot=BANK_STORAGE_SLOT))

    event_manager.process_msg(ExchangeLeaveEvent())

    assert not game_state_ctx.game_state.dialog.is_any_open


def test_changing_map_clears_the_state(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)
    event_manager.process_msg(ExchangeStartedWithStorageEvent(storage_max_slot=BANK_STORAGE_SLOT))

    event_manager.process_msg(MapCurrentEvent(map_id=1))

    assert not game_state_ctx.game_state.dialog.is_any_open


def test_an_open_bank_is_reused_instead_of_being_reopened(
    game_state_ctx: GameStateContext,
) -> None:
    event_manager, sent_messages = _make_event_manager(game_state_ctx)
    game_state_ctx.game_state.player.level = 200
    game_state_ctx.game_state.dialog.set_open(OpenDialogKind.BANK_STORAGE)
    auto_trip_behavior = MagicMock()
    behavior = EnterBankChestBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
        npc_dialog_behavior=MagicMock(),
        auto_trip_world_behavior=auto_trip_behavior,
    )
    finished: list[str | None] = []

    behavior.start(callback=finished.append, parent=None)

    assert finished == [None]
    assert sent_messages == []
    auto_trip_behavior.start.assert_not_called()


def _make_map_move_behavior(
    game_state_ctx: GameStateContext,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[MapMoveBehavior, list[Message]]:
    monkeypatch.setattr(
        MapState,
        "map_point",
        property(lambda _map_state: MapPoint.from_cell_id(START_CELL_ID)),
    )
    event_manager, sent_messages = _make_event_manager(game_state_ctx)
    behavior = MapMoveBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        path_finding=game_state_ctx.pathfinding,
        _logger=game_state_ctx.logger,
    )
    behavior.run_timer = _run_timer_inline
    return behavior, sent_messages


def _move_path() -> MovementPath:
    return MovementPath(
        start=MapPoint.from_cell_id(START_CELL_ID),
        end=MapPoint.from_cell_id(END_CELL_ID),
        path=MovementPath.get_path_elements_from_cells([START_CELL_ID, END_CELL_ID]),
    )


def test_moving_closes_whatever_is_still_open_first(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)
    game_state_ctx.game_state.dialog.set_open(OpenDialogKind.BANK_STORAGE)

    behavior.start(callback=None, parent=None, move_path=_move_path())

    assert [type(message) for message in sent_messages] == [DialogLeaveRequest]

    game_state_ctx.game_state.dialog.clear_state()
    behavior.event_manager.process_msg(ExchangeLeaveEvent())

    assert [type(message) for message in sent_messages] == [DialogLeaveRequest, MapMovementRequest]


def test_moving_with_nothing_open_goes_straight_ahead(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)

    behavior.start(callback=None, parent=None, move_path=_move_path())

    assert [type(message) for message in sent_messages] == [MapMovementRequest]


def test_leaving_a_dialog_that_is_not_open_sends_nothing(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)
    left: list[ExchangeLeaveEvent] = []

    behavior.start(callback=None, parent=None, move_path=_move_path())
    sent_messages.clear()
    behavior.leave_dialog(on_leave_callback=left.append)

    assert sent_messages == []
    assert len(left) == 1


def test_closing_a_npc_dialog_waits_for_the_dialog_leave_event(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)
    behavior.start(callback=None, parent=None, move_path=_move_path())
    game_state_ctx.game_state.dialog.set_open(OpenDialogKind.NPC_DIALOG)
    closed: list[bool] = []
    sent_messages.clear()

    behavior.ensure_dialog_closed(lambda: closed.append(True))

    assert [type(message) for message in sent_messages] == [DialogLeaveRequest]
    assert closed == []

    behavior.event_manager.process_msg(DialogLeaveEvent())

    assert closed == [True]
