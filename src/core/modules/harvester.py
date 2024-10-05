import random
from dataclasses import dataclass

from src.common.logger import Logger
from src.core.behaviors.collect_behavior import CollectBehavior
from src.core.behaviors.movements.auto_trip_behavior import AutoTripBehavior
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.repositories.world_graph_reader import WorldGraphReader
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.player_state import PlayerState
from src.interfaces.models.collectable import Collectable
from src.signals.harvester_signals import HarvesterSignals


@dataclass
class Harvester:
    collect_behavior: CollectBehavior
    auto_trip_behavior: AutoTripBehavior
    harvester_signals: HarvesterSignals
    path_finding: Pathfinding
    interactive_state: InteractiveState
    player_state: PlayerState
    inventory_state: InventoryState

    def __post_init__(self):
        self.harvester_signals.play.connect(self.start)
        self.harvester_signals.stop.connect(self.on_stop)

    def on_stop(self):
        Logger().info("Stopping Harvester")
        if self.collect_behavior.is_running.is_set():
            self.collect_behavior.stop()
        if self.auto_trip_behavior.is_running.is_set():
            self.auto_trip_behavior.stop()

    def start(self):
        Logger().info("Starting Harvester")
        self.collect_all()

    def collect_all(self):
        collectables = self.player_state.get_farmable_collectables()
        collectable_info = self.get_near_collectable(collectables)
        if collectable_info is None:
            next_map_id = self.get_random_next_map_id()
            Logger().info(f"No collectable found at this map, moving to {next_map_id}")
            self.auto_trip_behavior.start(callback=self.collect_all, map_id=next_map_id)
        else:
            move_path, collectable = collectable_info
            self.collect_behavior.start(
                callback=self.collect_all, move_path=move_path, collectable=collectable
            )

    def get_random_next_map_id(self) -> int:
        return random.choice(
            WorldGraphReader().get_outgoing_edges_from_vertex(
                self.player_state.curr_vertex
            )
        ).m_to.m_mapId

    def get_near_collectable(
        self,
        collectables: list[Collectable],
    ) -> tuple[MovementPath, Collectable] | None:
        near_move_path: tuple[MovementPath, Collectable, float] | None = None
        for collectable in collectables:
            move_path = self.path_finding.get_near_path_to_reachable_interactive(
                collectable.interactive_element.interactive_element.element_id,
                collectable.skill.skill_id,
            )
            if move_path is None:
                continue
            total_duration = move_path.get_total_duration(
                self.player_state.is_riding,
                self.inventory_state.inventory_weight,
                self.inventory_state.weight_max,
            )
            if near_move_path is None or total_duration < near_move_path[-1]:
                near_move_path = (move_path, collectable, total_duration)

        return near_move_path[:-1] if near_move_path else None
