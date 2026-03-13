import dataclasses
from dataclasses import dataclass, field

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.map_positions_root import MapInformationRootItem
from DBDofusUnity.dofus_unity_reader.models.world_graph import Vertice
from src.core import config
from src.core.engine.movements.world.linked_zone import get_linked_zone_rp
from src.core.engine.movements.world.transition_ban import BannedTransition, TransitionBanScope
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
    banned_edge_transitions: set[BannedTransition] = field(init=False, default_factory=set[BannedTransition])
    is_waiting_for_map_popup_dialog_leave: bool = field(init=False, default=False)
    _anomaly_info_requested: bool = field(init=False, default=False)

    def clear_state(self):
        self.is_in_map_transition = False
        self.is_in_haven_bag = False
        self.excluded_element_ids.clear()
        self.banned_edge_transitions.clear()
        self.is_waiting_for_map_popup_dialog_leave = False
        self._anomaly_info_requested = False

    def discard_map_stay_banned_transitions(self) -> None:
        self.banned_edge_transitions.difference_update(
            {ban for ban in self.banned_edge_transitions if ban.scope is TransitionBanScope.MAP_STAY}
        )

    @property
    def has_session_banned_transitions(self) -> bool:
        return any(ban.scope is TransitionBanScope.SESSION for ban in self.banned_edge_transitions)

    @property
    def is_in_map_transition(self) -> int:
        return self._is_in_map_transition

    @is_in_map_transition.setter
    def is_in_map_transition(self, value: bool):
        self._is_in_map_transition = value
        if config.DEBUG:
            self.grid_signals.is_in_map_transition.emit(value)

    @property
    def map_id(self) -> int:
        return self._map_id

    @map_id.setter
    def map_id(self, value: int):
        self._map_id = value
        if config.DEBUG:
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
        if config.DEBUG:
            self.game_info_signals.is_in_haven_bag.emit(value)

    @property
    def map_point(self):
        return MapPoint.from_cell_id(
            self.entity_state.actor_by_id[self.player_state.character_id].disposition.cell_id
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
