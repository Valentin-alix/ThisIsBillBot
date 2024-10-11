from dataclasses import dataclass, field
from enum import StrEnum, auto

from models.world_graph import Edge
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.edge_behavior import EdgeBehavior, EdgeError
from src.core.logic.world.edge import (
    draw_edge_path,
)
from src.core.logic.world.world_path_finder import WorldPathFinder
from src.exceptions import UnhandledErrorCodeException
from src.signals.world_signals import WorldSignals


class AutoTripErrorCode(StrEnum):
    PATH_NOT_FOUND = auto()


@dataclass
class AutoTripBehavior(Behavior):
    """auto trip by walking"""

    edge_behavior: EdgeBehavior
    world_path_finder: WorldPathFinder
    world_signals: WorldSignals

    auto_trip_edges: list[Edge] | None = field(default=None, init=False)
    target_map_ids: set[int] | None = field(default=None, init=False)

    def run(self, map_ids: set[int] | None = None, edge_path: list[Edge] | None = None):
        if map_ids is not None:
            self.logger.info(f"Auto trip to map id : {map_ids}")
            self.target_map_ids = map_ids
            path = self.world_path_finder.find_path(
                self.game_state.player.curr_vertex, map_ids
            )
            if path is None:
                return self.finish(AutoTripErrorCode.PATH_NOT_FOUND)
            if len(path) == 0:
                return self.finish()
            self.auto_trip_edges = path
            draw_edge_path(self.world_signals, self.auto_trip_edges)
        else:
            if edge_path is None:
                raise ValueError("no edge path provided")
            self.target_map_ids = {edge_path[-1].m_to.m_mapId}
            self.auto_trip_edges = edge_path
            draw_edge_path(self.world_signals, self.auto_trip_edges)

        self.process_edge()

    def process_edge(self):
        if self.auto_trip_edges is None or len(self.auto_trip_edges) == 0:
            return self.finish()

        edge = self.auto_trip_edges.pop(0)
        self.edge_behavior.start(
            callback=self.on_edge_behavior_finished, parent=self, edge=edge
        )

    def on_edge_behavior_finished(self, error_code: str | None):
        if error_code is EdgeError.INVALID_TRANSITION:
            return self.run(map_ids=self.target_map_ids)
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.process_edge()
