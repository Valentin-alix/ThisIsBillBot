import random
from collections import defaultdict
from functools import cache

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.characteristic import EffectElement

from src.core.engine.items.equipment import get_current_best_set, get_item_gids_to_buy

SET_DROP_REPEAT_PENALTY = 3


@cache
def _sub_area_ids_by_drop_gid() -> dict[int, frozenset[int]]:
    sub_areas_by_gid: defaultdict[int, set[int]] = defaultdict(set)
    for monster in DataReader().monsters_by_id.values():
        sub_areas = set(monster.subareas) or {monster.favoriteSubareaId}
        for drop in monster.drops:
            sub_areas_by_gid[drop.objectId].update(sub_areas)
    return {gid: frozenset(sub_areas) for gid, sub_areas in sub_areas_by_gid.items()}


def get_missing_set_drop_sub_area_ids(
    primary_elem: EffectElement,
    player_level: int,
    is_sub: bool,
    object_by_uid: dict[int, ObjectItemInventory],
) -> frozenset[int]:
    best_set = get_current_best_set(primary_elem, player_level, is_sub)
    if best_set is None:
        return frozenset()

    owned_gids = {object_item.item.gid for object_item in object_by_uid.values()}
    missing_gids = [
        item_info.item_gid
        for item_info in get_item_gids_to_buy(best_set, object_by_uid)
        if item_info.item_gid not in owned_gids
    ]

    sub_areas_by_gid = _sub_area_ids_by_drop_gid()
    sub_area_ids: set[int] = set()
    for gid in missing_gids:
        sub_area_ids |= sub_areas_by_gid.get(gid, frozenset())
    return frozenset(sub_area_ids)


def choose_set_drop_sub_area_id(
    missing_sub_area_ids: frozenset[int],
    player_level: int,
    previous_sub_area_ids: list[int],
) -> int | None:
    sub_area_by_id = DataReader().sub_area_by_id
    reachable_sub_area_ids = [
        sub_area_id
        for sub_area_id in missing_sub_area_ids
        if sub_area_id in sub_area_by_id
        and sub_area_by_id[sub_area_id].level <= player_level
    ]
    if not reachable_sub_area_ids:
        return None

    def selection_key(sub_area_id: int) -> tuple[int, float]:
        repeat = previous_sub_area_ids.count(sub_area_id)
        level = sub_area_by_id[sub_area_id].level
        return (level - repeat * SET_DROP_REPEAT_PENALTY, random.random())

    return max(reachable_sub_area_ids, key=selection_key)
