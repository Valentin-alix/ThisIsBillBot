import random

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from DBDofusUnity.dofus_unity_reader.data_center.area_info import (
    AREAS_SUB_WITH_WEIGHT,
    AREAS_UNSUB_WITH_WEIGHT,
    AreaInfo,
)
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from src.controller.game_data import GameDataController
from src.core.engine.contexts import HarvesterAreaContext
from src.core.engine.weights.harvester.weight_collectable import (
    get_weight_collectable,
)
from src.services.logging_utils.loggers import BotLogger


def get_fast_weight_harvester_sub_area(
    job_lvl_by_id: dict[int, int],
    storage_by_gid: dict[int, ObjectItemInventory],
    sub_area_id: int,
    is_sub: bool,
    job_id_by_item_id: dict[int, int],
    server_id: int = 1,
) -> float:
    harvestables = DataReader().sub_area_by_id[sub_area_id].harvestables
    if not harvestables:
        return 0

    weight = sum(
        get_weight_collectable(
            job_id,
            job_lvl_by_id.get(job_id, 1),
            item_id,
            storage_by_gid,
            is_sub,
            server_id,
        )
        for item_id in harvestables
        if (job_id := job_id_by_item_id.get(item_id)) is not None
    )
    return weight / len(harvestables)


def is_valid_area_info_to_harvest(
    area_info: AreaInfo,
    context: HarvesterAreaContext,
    weight_by_areas_info: dict[AreaInfo, float],
):
    return (
        context.player_level >= area_info.min_lvl
        and (
            area_info.waypoint_map_id_needed is None
            or area_info.waypoint_map_id_needed in context.player_waypoint_map_ids
        )
        and weight_by_areas_info[area_info] > 0
    )


def get_random_best_area_info(
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

    accessible_area_infos = [
        area_info
        for area_info in areas_with_weight
        if context.player_level >= area_info.min_lvl
        and (
            area_info.waypoint_map_id_needed is None
            or area_info.waypoint_map_id_needed in context.player_waypoint_map_ids
        )
    ]
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

    job_id_by_item_id = {
        item_id: job_id for item_id, job_id in GameDataController().get_item_job_by_gfx().values()
    }
    job_lvl_by_id = dict(context.player_jobs_lvl_by_id)
    storage_by_gid = dict(context.bank_storage_by_gid)

    for area_info in accessible_area_infos:
        if area_info.sub_area_id:
            weight = get_fast_weight_harvester_sub_area(
                job_lvl_by_id,
                storage_by_gid,
                area_info.sub_area_id,
                context.player_is_sub,
                job_id_by_item_id,
                server_id,
            )
        else:
            weight = sum(
                get_fast_weight_harvester_sub_area(
                    job_lvl_by_id,
                    storage_by_gid,
                    sub_area_id,
                    context.player_is_sub,
                    job_id_by_item_id,
                    server_id,
                )
                for sub_area_id in DataReader().sub_areas_by_area_id[area_info.area_id]
            )
        count_area_already_playing = server_area_infos.count(area_info)
        weight_by_areas_info[area_info] = (weight * area_info.weight_multiplier) / (
            1 + count_area_already_playing * 3 + previous_area_info_played.count(area_info)
        )

    areas_infos = [
        area_info
        for area_info in accessible_area_infos
        if is_valid_area_info_to_harvest(area_info, context, weight_by_areas_info)
    ]

    areas_weights = [
        (weight_by_areas_info[area_info])
        for area_info in accessible_area_infos
        if is_valid_area_info_to_harvest(area_info, context, weight_by_areas_info)
    ]

    logger.info(f"Area infos : {repr(areas_infos)} | Weight : {areas_weights}")

    return random.choices(areas_infos, weights=areas_weights, k=1)[0]
