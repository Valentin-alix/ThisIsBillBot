import dataclasses
from dataclasses import dataclass

from data_center.data_reader import DataReader
from models.datas.map_positions_root import MapPositionsRootItem

from src.core.states.state import State
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals


@dataclass
class MapState(State):
    grid_signals: GridSignals
    game_info_signals: GameInfoSignals
    phoenix_map_id: int = dataclasses.field(init=False, default=0)
    _is_in_map_transition: bool = dataclasses.field(init=False, default=False)
    _map_id: int = dataclasses.field(init=False, default=0)
    _is_in_haven_bag: bool = dataclasses.field(init=False, default=False)

    def clear_state(self):
        self.phoenix_map_id = 0
        self.is_in_haven_bag = False
        self._is_in_map_transition = False
        self._map_id = 0

    @property
    def is_in_map_transition(self) -> int:
        return self._is_in_map_transition

    @is_in_map_transition.setter
    def is_in_map_transition(self, value: bool):
        self._is_in_map_transition = value
        self.grid_signals.is_in_map_transition.emit(value)

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

    @property
    def is_in_haven_bag(self) -> bool:
        return self._is_in_haven_bag

    @is_in_haven_bag.setter
    def is_in_haven_bag(self, value: bool):
        self._is_in_haven_bag = value
        self.game_info_signals.is_in_haven_bag.emit(value)
