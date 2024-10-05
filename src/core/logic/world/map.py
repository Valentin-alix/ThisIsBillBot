from dataclasses import dataclass

from db_dofus_unity.gen.gen_datas import MapPositionsRoot
from src.core.repositories.data_reader import DataReader


@dataclass
class Map:
    map_id: int

    @property
    def position(self) -> MapPositionsRoot.Data:
        return DataReader().map_pos_by_map_id.get(self.map_id)
