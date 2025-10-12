from collections import defaultdict
from functools import cache
from math import log1p

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.game_constants.job import JobEnum
from DBDofusUnity.dofus_unity_reader.game_constants.monster import PROTECTOR_RACES

from src.controller.game_data import GameDataController
from src.core.config import WEIGHT_BY_JOB
from src.core.engine.monsters.drops import get_rare_gid_with_weight_from_protector_drop
from src.core.engine.movements.map.map_tools import MapTools

PRICE_EXPONENT = 1.1


def get_weight_collectable_for_sale_hotel(
    item_gid: int,
    avg_price_by_gid: dict[int, float],
    storage_object_by_item: dict[int, ObjectItemInventory],
    item_sell_quantity_by_gid: dict[int, int],
):

    return (
        avg_price_by_gid.get(item_gid, 1)
        * (related_object.item.quantity if (related_object := storage_object_by_item.get(item_gid)) else 0)
        / (1 + log1p(item_sell_quantity_by_gid.get(item_gid, 0)))
    )


def get_map_id_collectable_weight(
    map_id: int,
    player_job_lvl_by_id: dict[int, int],
    storage_by_gid: dict[int, ObjectItemInventory],
    is_sub: bool,
    server_id: int = 1,
) -> float:
    item_job_by_gfx = GameDataController().get_item_job_by_gfx()
    weight_map: float = 0
    for ref_id in MapReader().map_by_id(map_id).references:
        if ref_id.transform is None:
            continue
        if MapTools.is_transform_outside_map(ref_id.transform):
            continue
        if ref_id.gfxId is None:
            continue
        info = item_job_by_gfx.get(ref_id.gfxId)
        if info is None:
            continue
        item_id, job_id = info
        item = DataReader().item_by_id[item_id]
        job_lvl = player_job_lvl_by_id.get(job_id, 1)
        if item.level is None or item.level > job_lvl:
            continue
        weight_item = get_weight_collectable(job_id, job_lvl, item_id, storage_by_gid, is_sub, server_id)
        weight_map += weight_item
    return weight_map


def get_weight_collectable(
    job_id: int,
    job_lvl: int,
    item_gid: int,
    storage_by_gid: dict[int, ObjectItemInventory],
    is_sub: bool,
    server_id: int = 1,
):
    avg_price_by_gid = GameDataController().get_avg_price_by_gid(server_id)
    rare_drop_weight_by_collectable_gid = get_rare_drop_weight_by_collectable_gid()

    base = get_basic_weight_collectable(job_id, job_lvl, item_gid, is_sub)

    base += rare_drop_weight_by_collectable_gid.get(item_gid, 0) / 50

    price = avg_price_by_gid.get(item_gid, 1)
    if price <= 0:
        return 1

    scaled_price = price**PRICE_EXPONENT
    weight = base * scaled_price
    storage_qty = related_object.item.quantity if (related_object := storage_by_gid.get(item_gid)) else 0
    return weight / (1 + log1p(storage_qty))


@cache
def get_basic_weight_collectable(job_id: JobEnum, job_lvl: int, item_gid: int, is_sub: bool):
    item = DataReader().item_by_id[item_gid]
    if item.level is None or item.id is None:
        return 0

    weight = WEIGHT_BY_JOB[job_id]
    max_job_lvl = 200 if is_sub else 60
    if job_lvl != max_job_lvl:
        weight = weight * item.level * (((max_job_lvl + 1 - job_lvl) ** 2) if job_id != JobEnum.BASE else 1)

    return weight


@cache
def get_rare_drop_weight_by_collectable_gid() -> dict[int, float]:
    drop_weight_by_res_id: dict[int, float] = defaultdict(float)
    for race in PROTECTOR_RACES:
        for monster in DataReader().monsters_by_race[race]:
            res_object_id, curr_weight = get_rare_gid_with_weight_from_protector_drop(monster.drops)
            if res_object_id is None:
                continue
            drop_weight_by_res_id[res_object_id] = curr_weight

    return drop_weight_by_res_id
