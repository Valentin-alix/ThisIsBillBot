import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

import msgspec

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from DBDofusUnity.consts import MAPS_ARCHIVE_PATH
from DBDofusUnity.dofus_unity_reader.models.maps import CellData, MapDataRoot, MapReference
from utils.cache import cache
from utils.singleton import Singleton

zip_file = ZipFile(MAPS_ARCHIVE_PATH)
_MAP_CACHE_SIZE = 128


@dataclass(frozen=True)
class MapReader(metaclass=Singleton):
    @lru_cache(maxsize=_MAP_CACHE_SIZE)
    def map_by_id(self, map_id: int) -> MapDataRoot:
        return msgspec.json.decode(zip_file.read(f"map/map_{map_id}.json"), type=MapDataRoot)

    @staticmethod
    @cache
    def get_all_map_bundle_ids() -> set[int]:
        return {
            int(path.removeprefix("map/map_").removesuffix(".json"))
            for path in zip_file.namelist()
            if path.startswith("map/map_") and path.endswith(".json")
        }

    @cache
    def is_map_using_new_movement_system(self, map_id: int) -> bool:
        map_data = self.map_by_id(map_id)
        move_zone: int | None = None
        for cell_data in map_data.mapData.cellsData:
            if move_zone is None:
                move_zone = cell_data.moveZone
                continue
            if move_zone != cell_data.moveZone:
                return True
        return False

    @lru_cache(maxsize=_MAP_CACHE_SIZE)
    def get_ref_data_by_element_id_by_map_id(self, map_id: int) -> dict[int, MapReference]:
        return {
            ref.m_interactionId: ref
            for ref in self.map_by_id(map_id).references
            if ref.m_interactionId is not None
        }

    def get_cell_data_by_cell_id(self, map_id: int, cell_id: int) -> CellData:
        return self.map_by_id(map_id).mapData.cellsData[cell_id]
