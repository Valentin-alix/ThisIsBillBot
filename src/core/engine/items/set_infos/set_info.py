from functools import cached_property

from dofus_unity_reader.game_constants.characteristic import EffectElement
from dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)
from pydantic import BaseModel

from src.core.engine.economy.sale_hotel import ItemToBuyInfo

type ItemByPosition = dict[CharacterInventoryPositionEnum, ItemToBuyInfo]
type PositionByItemId = dict[int, CharacterInventoryPositionEnum]


class SetOnLevel(BaseModel):
    min_level: int
    elem: EffectElement
    item_info_by_position: ItemByPosition

    @cached_property
    def position_by_item_id(self) -> PositionByItemId:
        return {value.item_gid: key for key, value in self.item_info_by_position.items()}
