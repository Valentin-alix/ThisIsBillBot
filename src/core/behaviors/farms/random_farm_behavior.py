import random
from dataclasses import dataclass, field
from datetime import datetime
from time import sleep

from src.common.logger import Logger
from src.consts import MIN_DATE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip_behavior import AutoTripBehavior
from src.core.behaviors.movements.auto_trip_world_behavior import AutoTripWorldBehavior
from src.core.logic.world.edge import edge_has_valid_transitions
from src.core.repositories.world_graph_reader import WorldGraphReader, Edge
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState


@dataclass
class RandomFarmBehavior(Behavior):
    auto_trip_world_behavior: AutoTripWorldBehavior
    auto_trip_behavior: AutoTripBehavior
    player_state: PlayerState
    inventory_state: InventoryState
    map_state: MapState
    objective_state: ObjectiveState
    entity_state: EntityState

    last_visited_by_map_id: dict[int, datetime] = field(
        default_factory=dict, init=False
    )

    def run(self, map_ids: set[int]):
        """move to next map"""
        next_edge = self.get_random_next_edge(map_ids)
        if next_edge is None:
            Logger().info(f"Bot is not in target map ids, moving to target map ids")
            return self.auto_trip_world_behavior.start(
                callback=self.finish, parent=self, dst=map_ids
            )
        else:
            Logger().info(f"Moving to {next_edge.m_to}")
            self.auto_trip_behavior.start(
                callback=lambda error_code: (
                    self.finish() if error_code is None else self.run(map_ids)
                ),
                parent=self,
                dst=next_edge,
            )

    def get_random_next_edge(self, map_ids: set[int]) -> Edge | None:
        outgoing_edges = WorldGraphReader().get_outgoing_edges_from_vertex(
            self.player_state.curr_vertex
        )
        edges: list[Edge] = []
        Logger().info(f"Outgoing edges : {outgoing_edges}")
        for edge in outgoing_edges:
            if edge.m_to.m_mapId not in map_ids:
                continue
            if not edge_has_valid_transitions(
                edge,
                player_state=self.player_state,
                map_state=self.map_state,
                quest_state=self.objective_state,
                entity_state=self.entity_state,
                inventory_state=self.inventory_state,
            ):
                continue
            edges.append(edge)

        if len(edges) == 0:
            return None

        return self.get_weight_random_next_edge(edges)

    def get_weight_random_next_edge(self, edges: list[Edge]) -> Edge:
        chosen_edge: Edge = random.choices(
            edges, weights=[self.get_weight_map_id(edge.m_to.m_mapId) for edge in edges]
        )[0]
        self.last_visited_by_map_id[chosen_edge.m_to.m_mapId] = datetime.now()
        return chosen_edge

    def get_weight_map_id(self, map_id: int) -> float:
        last_visited = self.last_visited_by_map_id.get(map_id, MIN_DATE)
        return (datetime.now() - last_visited).total_seconds()


if __name__ == "__main__":
    last_visited = MIN_DATE
    sleep(1)
    temp = (datetime.now() - last_visited).total_seconds()
    print(temp)
