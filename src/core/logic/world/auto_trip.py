from dataclasses import dataclass

from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.astar import AStar
from src.core.repositories.world_graph_reader import WorldGraphReader, Edge
from src.core.states.entity_state import EntityState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.signals.player_signals import StatePropertySignals


@dataclass
class AutoTrip:
    path_finding: Pathfinding
    player_state: PlayerState
    map_state: MapState

    def find_path(
        self, dst_map_id: int, linked_zone: int | None = None
    ) -> list[Edge] | None:
        if linked_zone is None:
            linked_zone = 1
        src = self.player_state.curr_vertex
        if self.map_state.map.map_id == dst_map_id:
            return []

        while True:
            dst_vertex = WorldGraphReader().get_vertex(dst_map_id, linked_zone)
            if dst_vertex is None:
                return
            astar = AStar(
                path_finding=self.path_finding,
                src_vertex=src,
                dst_vertexes=[dst_vertex],
            )
            path = astar.search()
            if path:
                return path
            linked_zone += 1


if __name__ == "__main__":
    map_id = 189794311
    start = MapPoint.from_cell_id(356)
    # end = MapPoint.from_cell_id(91)

    is_in_fight = False
    state_property_signals = StatePropertySignals()
    map_state = MapState(state_property_signals=state_property_signals)
    entity_state = EntityState(state_property_signals=state_property_signals)
    player_state = PlayerState(
        map_state=map_state, state_property_signals=StatePropertySignals()
    )
    map_state.map.map_id = map_id

    data_map_provider = DataMapProvider(
        entity_state=entity_state, player_state=player_state, map_state=map_state
    )
    path_finding = Pathfinding(
        data_map_provider=data_map_provider,
        player_state=player_state,
        map_state=map_state,
    )
    auto_trip = AutoTrip(
        path_finding=path_finding, player_state=player_state, map_state=map_state
    )
    res = auto_trip.find_path(189793289)
    print(res)
