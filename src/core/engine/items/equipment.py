from functools import cached_property

from common_pb2 import ObjectItemInventory
from dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)
from dofus_unity_reader.game_constants.item import ItemEnum
from pydantic import BaseModel

from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.engine.items.item import get_equipment_on_position

type ItemByPosition = dict[CharacterInventoryPositionEnum, ItemToBuyInfo]
type PositionByItemId = dict[int, CharacterInventoryPositionEnum]


class SetOnLevel(BaseModel):
    min_level: int
    item_info_by_position: ItemByPosition

    @cached_property
    def position_by_item_id(self) -> PositionByItemId:
        return {
            value.item_gid: key for key, value in self.item_info_by_position.items()
        }


SET_BY_LEVEL_THRESHOLD: list[SetOnLevel] = [
    SetOnLevel(
        min_level=13,
        item_info_by_position={
            CharacterInventoryPositionEnum.AccessoryPositionHat: ItemToBuyInfo(
                item_gid=ItemEnum.CHAPEAU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionCape: ItemToBuyInfo(
                item_gid=ItemEnum.CAPE_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionAmulet: ItemToBuyInfo(
                item_gid=ItemEnum.AMU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingLeft: ItemToBuyInfo(
                item_gid=ItemEnum.ANNEAU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingRight: ItemToBuyInfo(
                item_gid=ItemEnum.ANNEAU_KARDORIM, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBelt: ItemToBuyInfo(
                item_gid=ItemEnum.CEINTURE_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBoots: ItemToBuyInfo(
                item_gid=ItemEnum.SANDALE_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionWeapon: ItemToBuyInfo(
                item_gid=ItemEnum.ARC_HOLLIS, max_kamas=2_000
            ),
        },
    ),
    SetOnLevel(
        min_level=43,
        item_info_by_position={
            CharacterInventoryPositionEnum.AccessoryPositionHat: ItemToBuyInfo(
                item_gid=ItemEnum.CHAPEAU_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionCape: ItemToBuyInfo(
                item_gid=ItemEnum.CAPE_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionAmulet: ItemToBuyInfo(
                item_gid=ItemEnum.AMULETTE_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingLeft: ItemToBuyInfo(
                item_gid=ItemEnum.ANNEAU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingRight: ItemToBuyInfo(
                item_gid=ItemEnum.ALLIANCE_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBelt: ItemToBuyInfo(
                item_gid=ItemEnum.CEINTURE_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBoots: ItemToBuyInfo(
                item_gid=ItemEnum.GETA_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionWeapon: ItemToBuyInfo(
                item_gid=ItemEnum.BATON_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionDofus1: ItemToBuyInfo(
                item_gid=ItemEnum.DOFUS_ARGENTE, max_kamas=60_000
            ),
        },
    ),
]


def get_current_best_set(level: int, is_sub: bool) -> SetOnLevel | None:
    available_set = [
        set_on_level
        for set_on_level in SET_BY_LEVEL_THRESHOLD
        if set_on_level.min_level <= level and (set_on_level.min_level <= 60 or is_sub)
    ]
    if not available_set:
        return None

    best_available_set = max(
        available_set, key=lambda set_on_level: set_on_level.min_level
    )
    return best_available_set


def get_item_gids_to_buy(
    set: SetOnLevel, object_by_uid: dict[int, ObjectItemInventory]
) -> list[ItemToBuyInfo]:

    item_info_to_buy: list[ItemToBuyInfo] = []
    for position, item_info in set.item_info_by_position.items():
        equipped_item = get_equipment_on_position(object_by_uid, position)
        if not equipped_item or equipped_item.item.gid != item_info.item_gid:
            item_info_to_buy.append(item_info)

    return item_info_to_buy
