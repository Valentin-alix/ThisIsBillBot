import dataclasses
from dataclasses import dataclass

from db_dofus_unity.gen.gen_datas import MapPositionsRoot
from src.core.repositories.data_reader import DataReader
from src.core.states.state import State
from src.signals.grid_signals import GridSignals


@dataclass
class MapState(State):
    grid_signals: GridSignals
    _map_id: int = dataclasses.field(init=False, default=0)

    @property
    def map_id(self) -> int:
        return self._map_id

    @map_id.setter
    def map_id(self, value: int):
        self._map_id = value
        self.grid_signals.new_map_id.emit(self._map_id)

    @property
    def map_pos(self) -> MapPositionsRoot.Data:
        return DataReader().map_pos_by_map_id[self.map_id]

    @property
    def sub_area_id(self):
        return self.map_pos.subAreaId
