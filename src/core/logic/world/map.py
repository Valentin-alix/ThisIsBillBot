from dataclasses import dataclass

from src.core.repositories.data_reader import DataReader


@dataclass
class Map:
    map_id: int

    @property
    def pos_x(self):
        return DataReader().map_pos_by_map_id[self.map_id].posX

    @property
    def pos_y(self):
        return DataReader().map_pos_by_map_id[self.map_id].posY

    @property
    def sub_area_id(self):
        return DataReader().map_pos_by_map_id[self.map_id].subAreaId
