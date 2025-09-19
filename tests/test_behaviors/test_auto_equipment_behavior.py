
from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

from datas.protos.non_obf.game.common_pb2 import (
    ObjectEffect,
    ObjectItem,
    ObjectItemInventory,
)
from dofus_unity_reader.game_constants.item import CategoryItemEnum, ItemEnum
from pytest import MonkeyPatch

from src.core.behaviors.equipment.auto_equipment_behavior import AutoEquipmentBehavior
from src.core.behaviors.items.acquire_items_behavior import ItemToAcquire
from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext

AMULETTE_AKWADALA_GID = int(ItemEnum.AMULETTE_AKWADALA)
MAX_KAMAS = 10_000
VITALITY_EFFECT_ACTION = 125


def _make_behavior(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> AutoEquipmentBehavior:
    game_state = game_state_ctx.game_state
    game_state.inventory.kamas = 1_000_000
    behavior = AutoEquipmentBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=EventManager(_logger=game_state_ctx.logger),
        game_state=game_state,
        _logger=game_state_ctx.logger,
        acquire_items_behavior=MagicMock(),
    )
    monkeypatch.setattr(
        behavior,
        "get_item_gids_to_equip",
        lambda: [ItemToBuyInfo(item_gid=AMULETTE_AKWADALA_GID, max_kamas=MAX_KAMAS)],
    )
    monkeypatch.setattr(
        type(game_state.player), "is_former_sub", property(lambda _player_state: True)
    )
    return behavior


def _mock_of(child_behavior: object) -> MagicMock:
    return cast(MagicMock, child_behavior)


def _child_kwarg(child_behavior: object, name: str) -> object:
    return _mock_of(child_behavior).start.call_args.kwargs[name]


def _copy(uid: int, roll: int) -> ObjectItemInventory:
    return ObjectItemInventory(
        item=ObjectItem(
            uid=uid,
            gid=AMULETTE_AKWADALA_GID,
            quantity=1,
            effects=[ObjectEffect(action=VITALITY_EFFECT_ACTION, value_int=roll)],
        )
    )


def _requested(behavior: AutoEquipmentBehavior) -> list[ItemToAcquire]:
    return cast(list[ItemToAcquire], _child_kwarg(behavior.acquire_items_behavior, "items"))


def _start(behavior: AutoEquipmentBehavior) -> None:
    behavior.start(callback=None, parent=None)


def _record_into(finished: list[str | None]) -> Callable[[str | None], None]:
    def callback(error_code: str | None) -> None:
        finished.append(error_code)

    return callback


def test_an_empty_slot_is_requested_without_upgrade_flag(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)

    _start(behavior)

    items = _requested(behavior)
    assert [(item.item_gid, item.quantity, item.upgrade_from_bank) for item in items] == [
        (AMULETTE_AKWADALA_GID, 1, False)
    ]
    assert items[0].category == CategoryItemEnum.EQUIPMENT
    assert items[0].max_kamas == MAX_KAMAS


def test_a_better_bank_copy_is_requested_as_an_upgrade(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    behavior.game_state.inventory.objects_by_uid[1] = _copy(uid=1, roll=10)
    behavior.game_state.inventory.bank_objects_by_uid[2] = _copy(uid=2, roll=50)
    behavior.game_state.inventory.bank_content_known = True

    _start(behavior)

    items = _requested(behavior)
    assert [(item.item_gid, item.quantity, item.upgrade_from_bank) for item in items] == [
        (AMULETTE_AKWADALA_GID, 1, True)
    ]


def test_a_worse_bank_copy_is_left_where_it_is(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    behavior.game_state.inventory.objects_by_uid[1] = _copy(uid=1, roll=50)
    behavior.game_state.inventory.bank_objects_by_uid[2] = _copy(uid=2, roll=10)
    behavior.game_state.inventory.bank_content_known = True
    collect_and_equip = MagicMock()
    monkeypatch.setattr(behavior, "collect_and_equip", collect_and_equip)

    _start(behavior)

    _mock_of(behavior.acquire_items_behavior).start.assert_not_called()
    collect_and_equip.assert_called_once_with()


def test_a_served_slot_is_left_alone_when_the_bank_is_out_of_reach(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    behavior.game_state.inventory.objects_by_uid[1] = _copy(uid=1, roll=10)
    behavior.game_state.inventory.bank_objects_by_uid[2] = _copy(uid=2, roll=50)
    behavior.game_state.inventory.bank_content_known = True
    behavior.game_state.inventory.kamas = 500
    collect_and_equip = MagicMock()
    monkeypatch.setattr(behavior, "collect_and_equip", collect_and_equip)

    _start(behavior)

    _mock_of(behavior.acquire_items_behavior).start.assert_not_called()
    collect_and_equip.assert_called_once_with()


def test_the_hourly_cooldown_still_holds(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    finished: list[str | None] = []

    behavior.start(callback=_record_into(finished), parent=None)
    behavior.on_items_acquired(None, {})
    _mock_of(behavior.acquire_items_behavior).start.reset_mock()

    behavior.start(callback=_record_into(finished), parent=None)

    _mock_of(behavior.acquire_items_behavior).start.assert_not_called()
    assert finished == [None, None]


def test_what_the_sourcing_could_not_find_does_not_abort_the_equipment(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    collect_and_equip = MagicMock()
    monkeypatch.setattr(behavior, "collect_and_equip", collect_and_equip)

    _start(behavior)
    behavior.on_items_acquired(None, {AMULETTE_AKWADALA_GID: 1})

    collect_and_equip.assert_called_once_with()
