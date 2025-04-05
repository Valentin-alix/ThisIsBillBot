import dataclasses
from dataclasses import dataclass, field

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.datas.map_positions_root import MapInformationRootItem
from dofus_unity_reader.models.world_graph import Transition, Vertice

from src import const
from src.core.engine.movements.world.linked_zone import get_linked_zone_rp
from src.core.signals.grid_signals import GridSignals
from src.core.signals.player_signals import GameInfoSignals
from src.core.states.entity_state import EntityState
from src.core.states.player_state import PlayerState
from src.core.states.state import State


@dataclass
class MapState(State):
    grid_signals: GridSignals
    player_state: PlayerState
    game_info_signals: GameInfoSignals
    entity_state: EntityState
    _is_in_map_transition: bool = dataclasses.field(init=False, default=False)
    _map_id: int = dataclasses.field(init=False, default=0)
    _is_in_haven_bag: bool = dataclasses.field(init=False, default=False)
    excluded_element_ids: set[int] = field(init=False, default_factory=set[int])
    forbidden_edge_transitions: set[tuple[Vertice, Vertice, Transition]] = field(
        init=False, default_factory=set[tuple[Vertice, Vertice, Transition]]
    )

    def clear_state(self):
        self.is_in_map_transition = False
        self._map_id = 0
        self.is_in_haven_bag = False
        self.excluded_element_ids.clear()
        self.forbidden_edge_transitions.clear()

    @property
    def is_in_map_transition(self) -> int:
        return self._is_in_map_transition

    @is_in_map_transition.setter
    def is_in_map_transition(self, value: bool):
        self._is_in_map_transition = value
        if const.DEBUG:
            self.grid_signals.is_in_map_transition.emit(value)

    @property
    def map_id(self) -> int:
        return self._map_id

    @map_id.setter
    def map_id(self, value: int):
        self._map_id = value
        if const.DEBUG:
            self.grid_signals.new_map_id.emit(self._map_id)

    @property
    def map_pos(self) -> MapInformationRootItem:
        return DataReader().map_info_by_map_id[self.map_id]

    @property
    def sub_area_id(self):
        return self.map_pos.subAreaId

    @property
    def is_in_haven_bag(self) -> bool:
        return self._is_in_haven_bag

    @is_in_haven_bag.setter
    def is_in_haven_bag(self, value: bool):
        self._is_in_haven_bag = value
        if const.DEBUG:
            self.game_info_signals.is_in_haven_bag.emit(value)

    @property
    def map_point(self):
        return MapPoint.from_cell_id(
            self.entity_state.actor_by_id[
                self.player_state.character_id
            ].disposition.cell_id
        )

    @property
    def linked_zone_rp(self) -> int:
        return get_linked_zone_rp(self.map_id, self.map_point.cell_id)

    @property
    def curr_vertex(self) -> Vertice:
        vertice = WorldGraphReader().get_vertex(self.map_id, self.linked_zone_rp)
        if vertice is None:
            potential_vertices = WorldGraphReader().get_vertexes(self.map_id)
            if len(potential_vertices) == 0:
                raise ValueError(
                    f"no vertice for map {self.map_id} at {self.map_point}, player is probably in fight"
                )
            vertice = next(iter(potential_vertices))
        return vertice
