import random

from datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from dofus_unity_reader.data_center.area_info import (
    AREAS_SUB_WITH_WEIGHT,
    AREAS_UNSUB_WITH_WEIGHT,
    AreaInfo,
)
from dofus_unity_reader.data_center.data_reader import DataReader

from src.core.engine.contexts import HarvesterAreaContext
from src.core.engine.weights.harvester.weight_collectable import (
    get_map_id_collectable_weight,
)
from src.services.logging_utils.loggers import BotLogger


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
        weight += get_map_id_collectable_weight(map_id, job_lvl_by_id, storage_by_gid, is_sub, server_id)
    count_map = len(DataReader().map_ids_by_sub_area_id[sub_area_id])
    if count_map == 0:
        return 0
    return int(weight / count_map)


def is_valid_area_info_to_harvest(
    area_info: AreaInfo,
    context: HarvesterAreaContext,
    weight_by_areas_info: dict[AreaInfo, float],
):
    return (
        context.player_level >= area_info.min_lvl
        and (
            area_info.waypoint_id_needed is None
            or area_info.waypoint_id_needed in context.player_waypoint_map_ids
        )
        and weight_by_areas_info[area_info] > 0
    )


def get_random_best_area_info_for_harvester(
    old_area_id: int | None,
    old_sub_area_id: int | None,
    context: HarvesterAreaContext,
    previous_area_info_played: list[AreaInfo],
    logger: BotLogger,
) -> AreaInfo:
    if old_area_id is not None:
        return AreaInfo(area_id=old_area_id, sub_area_id=old_sub_area_id)

    if context.player_is_sub:
        areas_with_weight = AREAS_SUB_WITH_WEIGHT
    else:
        areas_with_weight = AREAS_UNSUB_WITH_WEIGHT

    weight_by_areas_info: dict[AreaInfo, float] = {}

    server_id = context.player_server_id
    server_area_infos = [
        info
        for (
            srv_id,
            _,
        ), info in context.current_area_infos_by_server_and_character.items()
        if srv_id == server_id
    ]

    for area_info in areas_with_weight:
        if area_info.sub_area_id:
            weight = get_weight_harvester_sub_area(
                dict(context.player_jobs_lvl_by_id),
                dict(context.bank_storage_by_gid),
                area_info.sub_area_id,
                context.player_is_sub,
                server_id,
            )
        else:
            weight = get_weight_harvester_area(
                dict(context.player_jobs_lvl_by_id),
                area_info.area_id,
                context.player_is_sub,
                dict(context.bank_storage_by_gid),
                server_id,
            )
        count_area_already_playing = server_area_infos.count(area_info)
        weight_by_areas_info[area_info] = weight / (
            1 + count_area_already_playing * 3 + previous_area_info_played.count(area_info)
        )

    areas_infos = [
        area_info
        for area_info in areas_with_weight
        if is_valid_area_info_to_harvest(area_info, context, weight_by_areas_info)
    ]

    areas_weights = [
        (weight_by_areas_info[area_info])
        for area_info in areas_with_weight
        if is_valid_area_info_to_harvest(area_info, context, weight_by_areas_info)
    ]

    logger.info(f"Area infos : {repr(areas_infos)} | Weight : {areas_weights}")

    return random.choices(areas_infos, weights=areas_weights, k=1)[0]
