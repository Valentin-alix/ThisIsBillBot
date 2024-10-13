import dataclasses
from dataclasses import dataclass

from models.datas.map_positions_root import MapPositionsRootItem
from src.core.data_center.data_reader import DataReader
from src.core.states.state import State
from src.signals.grid_signals import GridSignals


@dataclass
class MapState(State):
    grid_signals: GridSignals
    phoenix_map_id: int = dataclasses.field(init=False, default=0)
    is_in_haven_bag: bool = dataclasses.field(init=False, default=False)
    is_in_map_transition: bool = dataclasses.field(init=False, default=False)
    _map_id: int = dataclasses.field(init=False, default=0)

    def clear_state(self):
        self.phoenix_map_id = 0
        self.is_in_haven_bag = False
        self.is_in_map_transition = False
        self._map_id = 0

    @property
    def map_id(self) -> int:
        return self._map_id

    @map_id.setter
    def map_id(self, value: int):
        self._map_id = value
        self.grid_signals.new_map_id.emit(self._map_id)

    @property
    def map_pos(self) -> MapPositionsRootItem:
        return DataReader().map_pos_by_map_id[self.map_id]

    @property
    def sub_area_id(self):
        return self.map_pos.subAreaId
