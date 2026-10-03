from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from google.protobuf.message import Message

from DBDofusUnity.datas.protos.non_obf.game.exchange_pb2 import ExchangeObjectMoveRequest
from DBDofusUnity.datas.protos.non_obf.game.guild_chest_pb2 import GuildChestTabSelectRequest
from DBDofusUnity.datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
    StorageInventoryContentEvent,
)
from DBDofusUnity.dofus_unity_reader.game_constants.item import ItemEnum
from src.core.behaviors.storage.unloads.unload_in_guild_chest_behavior import UnloadInGuildChestBehavior
from src.core.events_manager.event_manager import EventManager
from src.core.states import guild_chest_storage
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext
from tests.fixtures.inventory import make_inventory_item


@pytest.mark.parametrize("initial_tab", [1, 2], ids=["tab-content", "inventory-weight"])
def test_storage_event_resumes_transfers_once_after_the_delay(
    game_state_ctx: GameStateContext,
    monkeypatch: pytest.MonkeyPatch,
    initial_tab: int,
) -> None:
    monkeypatch.setattr(guild_chest_storage, "_STORAGE_REGISTRY", {})
    game_state = game_state_ctx.game_state
    game_state.guild_chest.tab_number = initial_tab
    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append
    behavior = UnloadInGuildChestBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=event_manager,
        game_state=game_state,
        _logger=game_state_ctx.logger,
        interactive_behavior=MagicMock(),
        path_finding=MagicMock(),
        auto_trip_world_behavior=MagicMock(),
        enter_guild_chest_behavior=MagicMock(),
    )
    pending_actions: list[Callable[[], None]] = []

    def schedule_action(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        pending_actions.append(func)

    behavior.run_timer = schedule_action
    items = [
        make_inventory_item(int(ItemEnum.GRAISSE_GELATINEUSE), quantity=10, uid=uid)
        for uid in (1, 2)
    ]
    behavior.object_to_unload_on_tab = [(2, items)]
    behavior.unload_tab()

    event: StorageInventoryContentEvent | InventoryWeightEvent
    if initial_tab == 1:
        pending_actions.pop(0)()
        assert sent_messages == [GuildChestTabSelectRequest(tab_number=2)]
        game_state.guild_chest.tab_number = 2
        event = StorageInventoryContentEvent()
        expected_uid = 2
    else:
        event = InventoryWeightEvent()
        expected_uid = 1

    sent_before_event = list(sent_messages)
    event_manager.process_msg(event)
    event_manager.process_msg(event)

    assert sent_messages == sent_before_event
    assert len(pending_actions) == 1
    pending_actions.pop(0)()
    assert sent_messages == [
        *sent_before_event,
        ExchangeObjectMoveRequest(object_uid=expected_uid, quantity=10),
    ]
    assert pending_actions == []
