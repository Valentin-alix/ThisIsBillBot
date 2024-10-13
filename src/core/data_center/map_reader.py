import os
import zlib
from dataclasses import dataclass

import msgspec

from D3Database.consts import D3_MAP
from models.maps import MapReference, CellData, MapDataRoot
from src.common.cache import cache
from src.interfaces.metaclasses.singleton import Singleton


@dataclass(frozen=True)
class MapReader(metaclass=Singleton):
    @cache
    def map_by_id(self, map_id: int) -> MapDataRoot:
        with open(os.path.join(D3_MAP, f"map_{map_id}.json"), "rb") as file:
            map_data = msgspec.json.decode(
                zlib.decompress(file.read()), type=MapDataRoot
            )
        return map_data

    @cache
    def is_map_using_new_movement_system(self, map_id: int) -> bool:
        map = self.map_by_id(map_id)
        move_zone: int | None = None
        for cell_data in map.mapData.cellsData:
            if move_zone is None:
                move_zone = cell_data.moveZone
                continue
            if move_zone != cell_data.moveZone:
                return True
        return False

    @cache
    def get_ref_data_by_element_id(self, map_id: int) -> dict[int, MapReference]:
        return {
            ref.m_interactionId: ref
            for ref in self.map_by_id(map_id).references
            if ref.m_interactionId is not None
        }

    @cache
    def get_ref_cell_data_by_cell_id(self, map_id: int) -> dict[int, MapReference]:
        return {
            ref.cellId: ref
            for ref in self.map_by_id(map_id).references
            if ref.cellId is not None
        }

    def get_cell_data_by_cell_id(self, map_id: int, cell_id: int) -> CellData:
        return self.map_by_id(map_id).mapData.cellsData[cell_id]
