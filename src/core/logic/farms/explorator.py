from data_center.data_reader import DataReader

from src.controller.gfx_mapping import GfxMappingController


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
