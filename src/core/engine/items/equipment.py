from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.game_constants.characteristic import EffectElement

from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.engine.items import set_infos
from src.core.engine.items.item import get_equipment_on_position


def get_current_best_set(
    elem: EffectElement, level: int, is_sub: bool
) -> set_infos.SetOnLevel | None:
    available_set = [
        set_on_level
        for set_on_level in set_infos.SET_BY_LEVEL_THRESHOLD
        if set_on_level.min_level <= level
        and (set_on_level.min_level <= 60 or is_sub)
        and set_on_level.elem == elem
    ]
    if not available_set:
        return None

    best_available_set = max(
        available_set, key=lambda set_on_level: set_on_level.min_level
    )
    return best_available_set


def get_item_gids_to_buy(
    set: set_infos.SetOnLevel, object_by_uid: dict[int, ObjectItemInventory]
) -> list[ItemToBuyInfo]:

    item_info_to_buy: list[ItemToBuyInfo] = []
    for position, item_info in set.item_info_by_position.items():
        equipped_item = get_equipment_on_position(object_by_uid, position)
        if not equipped_item or equipped_item.item.gid != item_info.item_gid:
            item_info_to_buy.append(item_info)

    return item_info_to_buy
