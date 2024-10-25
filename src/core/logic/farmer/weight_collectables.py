from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from d3_mapping.resources.protos.game.job_pb2 import JobExperiencesUpdateEvent
from data_center.data_reader import DataReader
from data_center.map_reader import MapReader
from enums.jobs_enum import HARVESTER_JOB_IDS, JobEnum

from src.core.config.weights import WEIGHT_BY_JOB
from src.core.controller.gfx_mapping import GfxMappingController
from src.core.logic.map.map_tools import MapTools
from src.signals.world_signals import WorldSignals


def get_weight_collectable(
    job_id: JobEnum,
    job_lvl: int,
    item_gid: int,
    avg_price_by_gid: dict[int, float],
    storage_by_gid: dict[int, ObjectItemInventory],
    is_sub: bool,
):
    item = DataReader().item_by_id[item_gid]
    if item.level is None:
        return 0

    weight = (
        WEIGHT_BY_JOB[job_id]
        * avg_price_by_gid.get(item_gid, 1)
        / (
            1 + related_object.item.quantity
            if (related_object := storage_by_gid.get(item_gid))
            else 1
        )
    )
    max_job_lvl = 200 if is_sub else 60
    if job_lvl != max_job_lvl:
        weight = (
            weight
            * item.level
            * (((max_job_lvl + 1 - job_lvl) ** 2) if job_id != JobEnum.BASE else 1)
        )

    return weight


def get_map_id_collectable_weight(
    map_id: int,
    gfx_to_item_and_job: dict[int, tuple[int, JobEnum]],
    player_job_lvl_by_id: dict[int, int],
    storage_by_gid: dict[int, ObjectItemInventory],
    avg_price_by_gid: dict[int, float],
    is_sub: bool,
) -> float:
    weight_map: float = 0
    for ref_id in MapReader().map_by_id(map_id).references:
        if ref_id.transform is None:
            continue
        if MapTools.is_transform_outside_map(ref_id.transform):
            continue
        if ref_id.gfxId is None:
            continue
        info = gfx_to_item_and_job.get(ref_id.gfxId)
        if info is None:
            continue
        item_id, job_id = info
        item = DataReader().item_by_id[item_id]
        job_lvl = player_job_lvl_by_id.get(job_id, 1)
        if item.level is None or item.level > job_lvl:
            continue
        weight_item = get_weight_collectable(
            job_id, job_lvl, item_id, avg_price_by_gid, storage_by_gid, is_sub
        )
        weight_map += weight_item
    return weight_map


def get_map_ids_to_explore(map_ids: set[int]) -> set[int]:
    map_ids_to_check: set[int] = set()

    map_id_checked: set[int] = GfxMappingController().get_map_ids_checked()
    item_knows = set(
        (
            item_id
            for item_id, _ in GfxMappingController().get_item_job_by_gfx().values()
        )
    )

    for map_id in map_ids:
        if map_id in map_id_checked:
            continue
        sub_area = DataReader().map_pos_by_map_id[map_id].subAreaId
        harvestable_items_sub_area = DataReader().sub_area_by_id[sub_area].harvestables
        for item in harvestable_items_sub_area:
            if item not in item_knows and item in DataReader().gathered_item_ids:
                map_ids_to_check.add(map_id)
                break

    return map_ids_to_check


def draw_weight_on_map(weight_by_map_id: dict[int, float], world_signals: WorldSignals):
    if len(weight_by_map_id) == 0:
        return
    max_weight = max(weight_by_map_id.values())
    world_signals.reset_weight.emit()
    for map_id, weight in weight_by_map_id.items():
        map_data = DataReader().map_pos_by_map_id[map_id]
        weight_color = int(255 * (weight / max_weight))
        world_signals.color_pos.emit(map_data, (255, 255 - weight_color, 0))


def is_interesting_job_lvl_up_for_weight(
    msg: JobExperiencesUpdateEvent, jobs_lvl_by_id: dict[int, int]
) -> bool:
    return any(
        job_xp.job_level % 10 == 0
        and jobs_lvl_by_id.get(job_xp.job_id, 1) != job_xp.job_level
        and job_xp.job_id in HARVESTER_JOB_IDS
        for job_xp in msg.experiences
    )
