import os
from dataclasses import dataclass
from functools import cache

import msgspec

from db_dofus_unity.consts import DOFUS_MAP_PATH
from db_dofus_unity.gen.gen_maps import MapsRoot
from src.interfaces.metaclasses.singleton import Singleton


@dataclass(frozen=True)
class MapReader(metaclass=Singleton):
    @cache
    def map_by_id(self, map_id: int) -> MapsRoot.Model:
        with open(os.path.join(DOFUS_MAP_PATH, f"map_{map_id}.json"), "rb") as file:
            map_data = msgspec.json.decode(file.read(), type=MapsRoot.Model)
        return map_data

    @cache
    def get_ref_data_by_element_id(self, map_id: int):
        return {
            ref_id_data.data.m_interactionId: ref_id_data.data
            for ref_id_data in self.map_by_id(map_id).references.RefIds
            if ref_id_data.data.m_interactionId
        }

    @cache
    def get_ref_cell_data_by_cell_id(self, map_id: int):
        return {
            ref_id_data.data.cellId: ref_id_data.data
            for ref_id_data in self.map_by_id(map_id).references.RefIds
        }

    def get_cell_data_by_cell_id(self, map_id: int, cell_id: int):
        return self.map_by_id(map_id).cellsData.Array[cell_id]
