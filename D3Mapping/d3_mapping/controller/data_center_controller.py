import os
from functools import cache

from D3Database.consts import D3_DATABASE
from D3Database.data_center.data_reader import DataReader
from D3Database.grid.map_point import MAP_POINT_BY_COORD

D3_DATABASE_PATH_MAP_FOLDER = os.path.join(D3_DATABASE, "bundles", "map")


class DataCenterController:
    POSSIBLE_COORD_X = {x for x, _ in MAP_POINT_BY_COORD.keys()}
    POSSIBLE_COORD_Y = {y for _, y in MAP_POINT_BY_COORD.keys()}
    POSSIBLE_ELEMENT_STATES = {0, 1, 2}
    SPELL_NUMEROS = {0, 1, 2}

    @staticmethod
    @cache
    def get_all_map_ids() -> set[int]:
        return set(DataReader().map_pos_by_map_id) | {
            int(file.replace(".json", "").split("map_")[1])
            for file in os.listdir(D3_DATABASE_PATH_MAP_FOLDER)
        }

    @staticmethod
    @cache
    def get_all_sub_area_ids() -> set[int]:
        return set(DataReader().sub_area_by_id)

    @staticmethod
    @cache
    def get_all_skill_ids() -> set[int]:
        return set(DataReader().skill_by_id)

    @staticmethod
    @cache
    def get_all_characteristic_ids() -> set[int]:
        return set(DataReader().characteristic_by_id)

    @staticmethod
    @cache
    def get_all_item_ids() -> set[int]:
        return set(DataReader().item_by_id)

    @staticmethod
    @cache
    def get_all_monster_gids() -> set[int]:
        return set(DataReader().monsters_by_id)

    @staticmethod
    @cache
    def get_all_spell_ids() -> set[int]:
        return set(DataReader().spell_by_id)

    @staticmethod
    @cache
    def get_all_spell_lvl_ids() -> set[int]:
        return set(DataReader().spell_lvl_by_id)

    @staticmethod
    @cache
    def get_all_type_item_ids() -> set[int]:
        return set(
            item.typeId for item in DataReader().item_by_id.values() if item.typeId
        )

    @staticmethod
    @cache
    def get_all_job_ids() -> set[int]:
        return set(DataReader().job_by_id)

    @staticmethod
    @cache
    def get_all_x_world_coodinates() -> set[int]:
        return set(x for x, _ in DataReader().map_pos_by_coord)

    @staticmethod
    @cache
    def get_all_y_world_coodinates() -> set[int]:
        return set(y for _, y in DataReader().map_pos_by_coord)

    @staticmethod
    @cache
    def get_all_key_cells() -> set[int]:
        key_cells: set[int] = set()
        for cell_id in range(560 + 1):
            for direction in range(8):
                key_cells.add(cell_id | direction << 12)
        return key_cells
