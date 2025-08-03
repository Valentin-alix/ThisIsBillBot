import random
from collections import defaultdict
from functools import cache

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.data_center.area_info import (
    AREAS_SUB_WITH_WEIGHT,
    AREAS_UNSUB_WITH_WEIGHT,
    AreaInfo,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.characteristic import EffectElement

from src.core.engine.items.equipment import get_current_best_set, get_item_gids_to_buy


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


def _covered_world_sub_area_id(area_info: AreaInfo, missing_sub_area_ids: frozenset[int]) -> int | None:
    """Sub-area of ``area_info`` that drops a missing set piece and is reachable
    by world navigation (overworld, not a dungeon), or None.

    Restricting to non-dungeon world-map sub-areas keeps the fighter on
    reachable maps (dungeon sub-areas were the original path_not_found cause).
    """
    sub_area_by_id = DataReader().sub_area_by_id
    area_sub_area_ids = DataReader().sub_areas_by_area_id.get(area_info.area_id, set())
    for sub_area_id in sorted(missing_sub_area_ids & area_sub_area_ids):
        sub_area = sub_area_by_id.get(sub_area_id)
        if sub_area is not None and sub_area.dungeonId <= 0 and sub_area.displayOnWorldMap:
            return sub_area_id
    return None


def choose_set_drop_area_info(
    missing_sub_area_ids: frozenset[int],
    player_level: int,
    is_sub: bool,
    waypoint_map_ids: frozenset[int],
    previous_area_infos: list[AreaInfo],
) -> AreaInfo | None:
    """Pick a reachable curated area whose monsters drop a missing set piece,
    narrowed to the exact sub-area that drops it.

    Only the curated candidates (the same ones the normal selection travels to
    reliably) are considered, so this never routes to an unreachable area. An
    area-level candidate is narrowed to the covered drop sub-area so the fighter
    farms exactly where the missing piece drops (e.g. Cité d'Astrub for the Piou
    set) instead of roaming the whole area.
    """
    if not missing_sub_area_ids:
        return None

    candidate_areas = AREAS_SUB_WITH_WEIGHT if is_sub else AREAS_UNSUB_WITH_WEIGHT
    matching_area_infos: list[AreaInfo] = []
    for area_info in candidate_areas:
        if player_level < area_info.min_lvl:
            continue
        if area_info.waypoint_id_needed is not None and area_info.waypoint_id_needed not in waypoint_map_ids:
            continue
        if area_info.sub_area_id is not None:
            if area_info.sub_area_id in missing_sub_area_ids:
                matching_area_infos.append(area_info)
            continue
        covered_sub_area_id = _covered_world_sub_area_id(area_info, missing_sub_area_ids)
        if covered_sub_area_id is not None:
            matching_area_infos.append(area_info.model_copy(update={"sub_area_id": covered_sub_area_id}))
    if not matching_area_infos:
        return None

    return min(
        matching_area_infos,
        key=lambda area_info: (previous_area_infos.count(area_info), random.random()),
    )
