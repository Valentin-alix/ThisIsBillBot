import random
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from src.common.logger import Logger
from src.core.behaviors.behavior import Behavior
from src.core.logic.world.edge import edge_has_valid_transitions
from src.core.repositories.world_graph_reader import WorldGraphReader
from src.core.states.entity_state import EntityState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState


@dataclass
class RandomFarmBehavior(Behavior, ABC):
    interactive_state: InteractiveState
    player_state: PlayerState
    inventory_state: InventoryState
    map_state: MapState
    objective_state: ObjectiveState
    entity_state: EntityState

    last_visited_by_map_id: dict[int, datetime] = field(
        default_factory=dict, init=False
    )

    def get_random_next_map_id(self) -> int:
        outgoing_edges = WorldGraphReader().get_outgoing_edges_from_vertex(
            self.player_state.curr_vertex
        )
        map_ids: list[int] = []
        Logger().info(f"Outgoing edges : {outgoing_edges}")
        for edge in outgoing_edges:
            if not edge_has_valid_transitions(
                edge,
                player_state=self.player_state,
                map_state=self.map_state,
                quest_state=self.objective_state,
                entity_state=self.entity_state,
                inventory_state=self.inventory_state,
            ):
                continue
            map_ids.append(edge.m_to.m_mapId)
        return self.get_weight_random_next_map_id(map_ids)

    def get_weight_random_next_map_id(self, map_ids: list[int]) -> int:
        chosen_map_id = random.choices(
            map_ids, weights=[self.get_weight_map_id(map_id) for map_id in map_ids]
        )[0]
        self.last_visited_by_map_id[chosen_map_id] = datetime.now()
        return chosen_map_id

    def get_weight_map_id(self, map_id: int):
        last_visited = self.last_visited_by_map_id.get(
            map_id, datetime.now() - timedelta(days=1)
        )
        return (datetime.now() - last_visited).total_seconds()
