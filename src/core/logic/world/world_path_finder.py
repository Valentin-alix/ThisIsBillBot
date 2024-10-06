from dataclasses import dataclass

from src.common.debugger import timeit
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.astar import AStar
from src.core.repositories.world_graph_reader import WorldGraphReader, Edge
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState
from src.signals.player_signals import StatePropertySignals


@dataclass
class WorldPathFinder:
    path_finding: Pathfinding
    player_state: PlayerState
    map_state: MapState
    quest_state: ObjectiveState
    entity_state: EntityState
    inventory_state: InventoryState

    @timeit
    def find_path(
        self, dst_map_id: int, linked_zone: int | None = None
    ) -> list[Edge] | None:
        if linked_zone is None:
            linked_zone = 1
        src_vertex = self.player_state.curr_vertex

        if self.map_state.map_id == dst_map_id:
            return []

        while True:
            dst_vertex = WorldGraphReader().get_vertex(dst_map_id, linked_zone)
            if dst_vertex is None:
                return None
            astar = AStar(
                path_finding=self.path_finding,
                src_vertex=src_vertex,
                dst_vertexes=[dst_vertex],
                player_state=self.player_state,
                map_state=self.map_state,
                quest_state=self.quest_state,
                entity_state=self.entity_state,
                inventory_state=self.inventory_state,
            )
            path = astar.search()
            if path:
                return path
            linked_zone += 1


if __name__ == "__main__":
    map_id = 188743682
    start = MapPoint.from_cell_id(349)

    is_in_fight = False
    state_property_signals = StatePropertySignals()
    interactive_state = InteractiveState(state_property_signals=state_property_signals)
    map_state = MapState(state_property_signals=state_property_signals)
    entity_state = EntityState(state_property_signals=state_property_signals)
    fight_state = FightState(state_property_signals=state_property_signals)
    player_state = PlayerState(
        map_state=map_state,
        state_property_signals=StatePropertySignals(),
        entity_state=entity_state,
        interactive_state=interactive_state,
        fight_state=fight_state,
    )
    quest_state = ObjectiveState(state_property_signals=StatePropertySignals())
    inventory_state = InventoryState(state_property_signals=StatePropertySignals())

    map_state.map_id = map_id

    data_map_provider = DataMapProvider(
        entity_state=entity_state,
        player_state=player_state,
        map_state=map_state,
        fight_state=fight_state,
    )
    path_finding = Pathfinding(
        data_map_provider=data_map_provider,
        player_state=player_state,
        map_state=map_state,
        entity_state=entity_state,
    )
    auto_trip = WorldPathFinder(
        path_finding=path_finding,
        player_state=player_state,
        map_state=map_state,
        quest_state=quest_state,
        inventory_state=inventory_state,
        entity_state=entity_state,
    )
    res = auto_trip.find_path(188744194)
    print(res)
