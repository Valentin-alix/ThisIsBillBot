import random

from d3_database.data_center.data_reader import DataReader
from d3_database.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)

from src.core.config import AREAS_SUB_WITH_WEIGHT, AREAS_UNSUB_WITH_WEIGHT
from src.core.engine.movements.area_infos import AreaInfo
from src.core.engine.weights.harvester.weight_collectable import (
    get_map_id_collectable_weight,
)
from src.core.states.area_state import (
    CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER,
)
from src.core.states.game_state import GameState
from src.services.logging.logger import Logger


def get_weight_harvester_area(
    job_lvl_by_id: dict[int, int],
    area_id: int,
    is_sub: bool,
    storage_by_gid: dict[int, ObjectItemInventory],
    server_id: int = 1,
):
    return sum(
        [
            get_weight_harvester_sub_area(
                job_lvl_by_id,
                storage_by_gid,
                sub_area_id,
                is_sub,
                server_id,
            )
            for sub_area_id in DataReader().sub_areas_by_area_id[area_id]
        ]
    )


def get_weight_harvester_sub_area(
    job_lvl_by_id: dict[int, int],
    storage_by_gid: dict[int, ObjectItemInventory],
    sub_area_id: int,
    is_sub: bool,
    server_id: int = 1,
):
    weight: float = 0
    for map_id in DataReader().map_ids_by_sub_area_id[sub_area_id]:
        weight += get_map_id_collectable_weight(
            map_id,
            job_lvl_by_id,
            storage_by_gid,
            is_sub,
            server_id,
        )
    return int(weight / len(DataReader().map_ids_by_sub_area_id[sub_area_id]))


def is_valid_area_info_to_harvest(
    area_info: AreaInfo,
    game_state: GameState,
    weight_by_areas_info: dict[AreaInfo, float],
):
    return (
        game_state.player.level >= area_info.min_lvl
        and (
            area_info.waypoint_id_needed is None
            or area_info.waypoint_id_needed in game_state.player.waypoint_map_ids
        )
        and weight_by_areas_info[area_info] > 0
    )


def get_random_best_area_info_for_harvester(
    old_area_id: int | None,
    old_sub_area_id: int | None,
    game_state: GameState,
    previous_area_info_played: list[AreaInfo],
    logger: Logger,
) -> AreaInfo:
    if old_area_id is not None:
        return AreaInfo(area_id=old_area_id, sub_area_id=old_sub_area_id)

    if game_state.player.is_sub:
        areas_with_weight = AREAS_SUB_WITH_WEIGHT
    else:
        areas_with_weight = AREAS_UNSUB_WITH_WEIGHT

    weight_by_areas_info: dict[AreaInfo, float] = {}

    server_id = game_state.player.server_id
    server_area_infos = [
        info
        for (
            srv_id,
            _,
        ), info in CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER.items()
        if srv_id == server_id
    ]

    for area_info in areas_with_weight:
        if area_info.sub_area_id:
            weight = get_weight_harvester_sub_area(
                game_state.player.jobs_lvl_by_id,
                game_state.inventory.bank_object_by_gid,
                area_info.sub_area_id,
                game_state.player.is_sub,
                server_id,
            )
        else:
            weight = get_weight_harvester_area(
                game_state.player.jobs_lvl_by_id,
                area_info.area_id,
                game_state.player.is_sub,
                game_state.inventory.bank_object_by_gid,
                server_id,
            )
        count_area_already_playing = server_area_infos.count(area_info)
        weight_by_areas_info[area_info] = weight / (
            1
            + count_area_already_playing * 3
            + previous_area_info_played.count(area_info)
        )

    areas_infos = [
        area_info
        for area_info in areas_with_weight
        if is_valid_area_info_to_harvest(area_info, game_state, weight_by_areas_info)
    ]

    areas_weights = [
        (weight_by_areas_info[area_info])
        for area_info in areas_with_weight
        if is_valid_area_info_to_harvest(area_info, game_state, weight_by_areas_info)
    ]

    logger.info(f"Area infos : {repr(areas_infos)} | Weight : {areas_weights}")

    return random.choices(areas_infos, weights=areas_weights, k=1)[0]
