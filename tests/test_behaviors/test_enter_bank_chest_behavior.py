from typing import Callable, cast
from unittest.mock import Mock

from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveEvent, DialogLeaveRequest
from google.protobuf.message import Message
from dofus_unity_reader.game_constants.npc import BANK_NPCS

from src.core.behaviors.npcs.npc_dialog_behavior import (
    NpcDialogBehavior,
    NpcDialogErrorCode,
)
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
    EnterBankChestErrorCode,
)
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext


def test_forbidden_bank_dialog_is_closed_before_not_enough_kamas_finish(
    game_state_ctx: GameStateContext,
) -> None:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append

    bank_npc_info = next(iter(BANK_NPCS))
    game_state_ctx.game_state.map.map_id = bank_npc_info.npc_map_id
    game_state_ctx.game_state.player.level = 37
    game_state_ctx.game_state.inventory.kamas = 105

    auto_trip_world_behavior = Mock()
    npc_dialog_behavior = Mock()

    def start_auto_trip(
        *,
        callback: Callable[[str | None], None],
        parent: object,
        map_ids: set[int],
    ) -> None:
        del parent, map_ids
        callback(None)

    def start_npc_dialog(
        *,
        callback: Callable[[str | None], None],
        parent: object,
        npc_dialog_info: object,
        is_forbidden_msg_callback: object,
    ) -> None:
        del parent, npc_dialog_info, is_forbidden_msg_callback
        callback(NpcDialogErrorCode.FORBIDDEN_CONDITION)

    auto_trip_world_behavior.start.side_effect = start_auto_trip
    npc_dialog_behavior.start.side_effect = start_npc_dialog

    finished_errors: list[str | None] = []
    behavior = EnterBankChestBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
        npc_dialog_behavior=cast(NpcDialogBehavior, npc_dialog_behavior),
        auto_trip_world_behavior=cast(AutoTripSmartBehavior, auto_trip_world_behavior),
    )

    behavior.start(callback=finished_errors.append, parent=None)

    assert finished_errors == []
    assert [type(message) for message in sent_messages] == [DialogLeaveRequest]

    event_manager.process_msg(DialogLeaveEvent())

    assert finished_errors == [EnterBankChestErrorCode.NOT_ENOUGH_KAMAS]
