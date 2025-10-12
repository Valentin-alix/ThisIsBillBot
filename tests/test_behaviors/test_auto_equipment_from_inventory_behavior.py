from collections.abc import Iterable

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import EffectElement
from DBDofusUnity.dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)
from pytest import MonkeyPatch

from src.core.behaviors.items.auto_equipment_from_inventory_behavior import (
    AutoEquipmentFromInventoryBehavior,
)
from src.core.behaviors.items import auto_equipment_from_inventory_behavior
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext


def _item(uid: int) -> ObjectItemInventory:
    return ObjectItemInventory(item=ObjectItem(uid=uid, gid=uid, quantity=1))


def test_best_loadout_keeps_a_pair_that_is_only_better_together(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = AutoEquipmentFromInventoryBehavior(
        event_manager=EventManager(_logger=game_state_ctx.logger),
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
    )
    hat = _item(1)
    cape = _item(2)
    dropped_hat = _item(3)
    dropped_cape = _item(4)
    scores_by_uids = {
        frozenset({1, 2}): 100.0,
        frozenset({3, 2}): 90.0,
        frozenset({1, 4}): 90.0,
        frozenset({3, 4}): 120.0,
    }
    def score(items: Iterable[ObjectItemInventory], _elem: EffectElement) -> float:
        return scores_by_uids[frozenset(item.item.uid for item in items)]

    def positions(gid: int) -> tuple[CharacterInventoryPositionEnum, ...]:
        return {
            3: (CharacterInventoryPositionEnum.AccessoryPositionHat,),
            4: (CharacterInventoryPositionEnum.AccessoryPositionCape,),
        }.get(gid, ())

    monkeypatch.setattr(
        auto_equipment_from_inventory_behavior,
        "equipment_score",
        score,
    )
    monkeypatch.setattr(
        auto_equipment_from_inventory_behavior,
        "get_equipment_positions",
        positions,
    )
    current = {
        CharacterInventoryPositionEnum.AccessoryPositionHat: hat,
        CharacterInventoryPositionEnum.AccessoryPositionCape: cape,
    }

    best = behavior._best_loadout(current, [dropped_hat, dropped_cape])

    assert best == {
        CharacterInventoryPositionEnum.AccessoryPositionHat: dropped_hat,
        CharacterInventoryPositionEnum.AccessoryPositionCape: dropped_cape,
    }
