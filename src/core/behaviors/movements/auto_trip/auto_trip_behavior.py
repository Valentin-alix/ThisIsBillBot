from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial

from datas.protos.non_obf.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from dofus_unity_reader.models.world_graph import Edge

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.edge_behavior import EdgeBehavior, EdgeError
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.movements.map_move_behavior import MapMoveError
from src.core.engine.movements.world.edge import (
    draw_edge_path,
)
from src.core.engine.movements.world.world_path_finder import WorldPathFinder
from src.core.signals.world_signals import WorldSignals


class AutoTripErrorCode(StrEnum):
    PATH_NOT_FOUND = auto()


_MAX_REPLAN_ON_DESYNC = 8


@dataclass
class AutoTripBehavior(Behavior):
    """auto trip by walking"""

    edge_behavior: EdgeBehavior
    world_path_finder: WorldPathFinder
    world_signals: WorldSignals

    auto_trip_edges: list[Edge] | None = field(default=None, init=False)
    target_map_ids: set[int] | None = field(default=None, init=False)
    _replan_on_desync: int = field(default=0, init=False)

    def run(
        self,
        map_ids: set[int] | None = None,
        edge_path: list[Edge] | None = None,
        from_auto_trip_zaap_behavior: bool = False,
        retry: int = 3,
    ) -> None:
        if self.game_state.map.is_in_map_transition:
            return self.event_manager.on(
                MapComplementaryInformationEvent,
                lambda _: self.finish(MapChangeError.UNEXPECTED_NEW_MAP),
                originator=self,
            )
        if self.game_state.fight.in_fight:
            return self.finish(MapChangeError.UNEXPECTED_NEW_MAP)
        if map_ids is not None:
            self.logger.info(f"Auto trip to map id : {map_ids}")
            self.target_map_ids = map_ids
            curr_vertex = self.game_state.map.curr_vertex
            path = self.world_path_finder.find_path(
                self.game_state.get_world_path_context(), curr_vertex, map_ids
            )
            if path is None:
                self.logger.warning(
                    f"Path not found from {self.game_state.map.curr_vertex} to {map_ids}"
                )
                if from_auto_trip_zaap_behavior or retry <= 0:
                    return self.finish(AutoTripErrorCode.PATH_NOT_FOUND)
                return self.run(
                    map_ids, edge_path, from_auto_trip_zaap_behavior, retry - 1
                )
            if len(path) == 0:
                self.logger.info("Path to these map ids is empty")
                return self.finish()
            self.auto_trip_edges = path
            draw_edge_path(self.world_signals, self.auto_trip_edges)
        else:
            if edge_path is None:
                raise ValueError("no edge path provided")
            if len(edge_path) == 0:
                self.logger.info("Path to these edge is empty")
                return self.finish()
            self.target_map_ids = {edge_path[-1].m_to.m_mapId}
            self.auto_trip_edges = edge_path
            draw_edge_path(self.world_signals, self.auto_trip_edges)

        self.process_edge()

    def process_edge(self) -> None:
        if self.auto_trip_edges is None or len(self.auto_trip_edges) == 0:
            self.logger.info("Empty auto trip edge")
            return self.finish()

        edge = self.auto_trip_edges.pop(0)
        self.edge_behavior.start(
            callback=self.on_edge_behavior_finished, parent=self, edge=edge
        )

    def on_edge_behavior_finished(self, error_code: str | None) -> None:
        if error_code in (
            EdgeError.NO_VALID_TRANSITION,
            EdgeError.INVALID_STARTING_MAP,
        ):
            self._replan_on_desync += 1
            if self._replan_on_desync > _MAX_REPLAN_ON_DESYNC:
                self.logger.warning(
                    f"Too many consecutive replans ({self._replan_on_desync}); "
                    "aborting trip"
                )
                return self.finish(error_code)
            return self.run(map_ids=self.target_map_ids)
        elif (
            error_code is not None and error_code is not MapMoveError.UNEXPECTED_NEW_MAP
        ):
            return self.finish(error_code)

        self._replan_on_desync = 0
        self.event_manager.on(
            MapComplementaryInformationEvent,
            partial(
                self.on_map_complementary_information_event_after_edge,
                error_code=error_code,
            ),
            originator=self,
            once=True,
            override_on_self=True,
        )

    def on_map_complementary_information_event_after_edge(
        self, msg: MapComplementaryInformationEvent, error_code: str | None
    ) -> None:
        if error_code is not None:
            return self.finish(error_code)
        self.process_edge()
