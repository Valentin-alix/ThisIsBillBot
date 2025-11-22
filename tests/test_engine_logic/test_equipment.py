from types import SimpleNamespace

import pytest
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ObjectEffect, ObjectItem, ObjectItemInventory
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import (
    CharacteristicEnum,
    EffectElement,
)
from DBDofusUnity.dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)

from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.engine.items import equipment as equipment_module
from src.core.engine.items.equipment import get_item_gids_to_buy
from src.core.engine.items.set_infos.set_info import SetOnLevel

_SET_ITEM_GID = 900
_FOREIGN_ITEM_GID = 901
_POWER_ACTION = 1
_AMULET_POSITION = CharacterInventoryPositionEnum.AccessoryPositionAmulet


@pytest.fixture(autouse=True)
def patch_data_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_data_reader = SimpleNamespace(
        effect_by_id={_POWER_ACTION: SimpleNamespace(characteristic=CharacteristicEnum.POWER)},
    )
    monkeypatch.setattr(equipment_module, "DataReader", lambda: fake_data_reader)


def _item(uid: int, gid: int, roll: int, position: CharacterInventoryPositionEnum) -> ObjectItemInventory:
    return ObjectItemInventory(
        position=position,
        item=ObjectItem(uid=uid, gid=gid, effects=[ObjectEffect(action=_POWER_ACTION, value_int=roll)]),
    )


def _amulet_set() -> SetOnLevel:
    return SetOnLevel(
        min_level=1,
        elem=EffectElement.STRENGTH,
        item_info_by_position={
            _AMULET_POSITION: ItemToBuyInfo(item_gid=_SET_ITEM_GID, max_kamas=10_000),
        },
    )


def test_an_empty_slot_needs_the_set_item() -> None:
    missing = get_item_gids_to_buy(_amulet_set(), {}, EffectElement.STRENGTH)

    assert [info.item_gid for info in missing] == [_SET_ITEM_GID]


def test_a_stronger_owned_foreign_item_already_equipped_is_left_alone() -> None:
    """Regression: AutoEquipmentFromInventoryBehavior swapped a stronger, non-set
    item into the slot, and we still own the weaker set item (displaced to the
    inventory, unequipped). The set must not fight that swap every cycle."""
    objects_by_uid = {
        1: _item(uid=1, gid=_FOREIGN_ITEM_GID, roll=20, position=_AMULET_POSITION),
        2: _item(uid=2, gid=_SET_ITEM_GID, roll=10, position=CharacterInventoryPositionEnum.InventoryPositionNotEquiped),
    }

    missing = get_item_gids_to_buy(_amulet_set(), objects_by_uid, EffectElement.STRENGTH)

    assert missing == []


def test_a_weaker_owned_copy_of_the_set_item_still_reclaims_the_slot() -> None:
    objects_by_uid = {
        1: _item(uid=1, gid=_FOREIGN_ITEM_GID, roll=5, position=_AMULET_POSITION),
        2: _item(uid=2, gid=_SET_ITEM_GID, roll=20, position=CharacterInventoryPositionEnum.InventoryPositionNotEquiped),
    }

    missing = get_item_gids_to_buy(_amulet_set(), objects_by_uid, EffectElement.STRENGTH)

    assert [info.item_gid for info in missing] == [_SET_ITEM_GID]


def test_an_unowned_set_item_still_replaces_a_foreign_equipped_item() -> None:
    objects_by_uid = {
        1: _item(uid=1, gid=_FOREIGN_ITEM_GID, roll=20, position=_AMULET_POSITION),
    }

    missing = get_item_gids_to_buy(_amulet_set(), objects_by_uid, EffectElement.STRENGTH)

    assert [info.item_gid for info in missing] == [_SET_ITEM_GID]


def test_the_set_item_already_equipped_needs_nothing() -> None:
    objects_by_uid = {
        1: _item(uid=1, gid=_SET_ITEM_GID, roll=10, position=_AMULET_POSITION),
    }

    missing = get_item_gids_to_buy(_amulet_set(), objects_by_uid, EffectElement.STRENGTH)

    assert missing == []
