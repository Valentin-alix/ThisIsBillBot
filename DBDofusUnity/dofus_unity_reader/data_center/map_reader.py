from dataclasses import dataclass

import msgspec
from base_python.cache import cache
from base_python.singleton import Singleton

from consts import MAP_BUNDLES_ROOT
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.models.maps import CellData, MapDataRoot, MapReference


@dataclass(frozen=True)
class MapReader(metaclass=Singleton):
    @cache
    def map_by_id(self, map_id: int) -> MapDataRoot:
        with (MAP_BUNDLES_ROOT / f"map_{map_id}.json").open("rb") as file:
            return msgspec.json.decode(file.read(), type=MapDataRoot)

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

    @cache
    def get_ref_data_by_element_id_by_map_id(self, map_id: int) -> dict[int, MapReference]:
        return {
            ref.m_interactionId: ref
            for ref in self.map_by_id(map_id).references
            if ref.m_interactionId is not None
        }

    @cache
    def get_ref_data_by_element_id(self) -> dict[int, MapReference]:
        ref_data_by_element_id: dict[int, MapReference] = {}
        map_ids = DataReader().map_info_by_map_id
        for map_id in map_ids:
            for ref in self.map_by_id(map_id).references:
                if ref.m_interactionId is not None:
                    ref_data_by_element_id[ref.m_interactionId] = ref
        return ref_data_by_element_id

    @cache
    def get_ref_cell_data_by_cell_id(self, map_id: int) -> dict[int, MapReference]:
        return {ref.cellId: ref for ref in self.map_by_id(map_id).references if ref.cellId is not None}

    def get_cell_data_by_cell_id(self, map_id: int, cell_id: int) -> CellData:
        return self.map_by_id(map_id).mapData.cellsData[cell_id]
