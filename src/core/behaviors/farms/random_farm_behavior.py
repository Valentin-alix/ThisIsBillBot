from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from time import sleep

from models.world_graph import Edge
from src.const import MIN_DATE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.movements.edge_behavior import EdgeBehavior
from src.core.data_center.data_reader import DataReader
from src.core.logic.farmer.weight_collectables import draw_weight_on_map
from src.core.logic.farmer.weighted_path import WeightedPath
from src.core.logic.world.edge import draw_edge_path
from src.exceptions import UnexpectedStateException
from src.signals.world_signals import WorldSignals

LAST_VISITED_BY_MAP_ID: dict[int, datetime] = {}


@dataclass
class RandomFarmBehavior(Behavior):
    auto_trip_world_behavior: AutoTripSmartBehavior
    edge_behavior: EdgeBehavior
    weighted_path: WeightedPath
    world_signals: WorldSignals

    additional_weight_by_map_id: dict[int, float] = field(
        default_factory=dict, init=False
    )

    map_ids: set[int] = field(default_factory=set, init=False)
    edge_path: list[Edge] | None = field(default=None, init=False)

    def init_random_farm(self, area_id: int | None, sub_area_id: int | None):
        self.additional_weight_by_map_id.clear()
        self.edge_path = None
        self.world_signals.reset_weight.emit()
        self.map_ids = self.get_map_ids(area_id, sub_area_id)

    def run(self):
        if self.game_state.map.map_id not in self.map_ids:
            self.logger.info(f"Bot is not in target map ids, moving to target map ids")
            return self.auto_trip_world_behavior.start(
                callback=self.on_auto_trip_world_behavior_finished,
                parent=self,
                map_ids=self.map_ids,
            )
        if (
            self.edge_path is None
            or len(self.edge_path) == 0
            or self.edge_path[0].m_from.m_mapId != self.game_state.map.map_id
        ):
            self.edge_path = self.get_next_weighted_path()
            draw_edge_path(self.world_signals, self.edge_path)
        edge = self.edge_path[0]
        self.edge_behavior.start(
            callback=partial(self.on_edge_behavior_finished, edge=edge),
            parent=self,
            edge=edge,
        )

    def get_map_ids(self, area_id: int | None, sub_area_id: int | None) -> set[int]:
        self.logger.info(
            f"init map ids based on area {area_id} and sub area {sub_area_id}"
        )
        if sub_area_id is not None:
            return set(DataReader().sub_area_by_id[sub_area_id].mapIds)
        elif area_id is not None:
            return DataReader().map_ids_by_area_id[area_id]
        return set(DataReader().sub_area_by_id[self.game_state.map.sub_area_id].mapIds)

    def on_edge_behavior_finished(self, error_code: str | None, edge: Edge):
        if self.edge_path is None:
            raise ValueError("edge path should not be none")
        if error_code is None:
            self.edge_path.remove(edge)
            LAST_VISITED_BY_MAP_ID[self.game_state.map.map_id] = datetime.now()
        else:
            self.edge_path = None
        self.finish(error_code)

    def on_auto_trip_world_behavior_finished(self, error_code: str | None):
        if error_code is None:
            LAST_VISITED_BY_MAP_ID[self.game_state.map.map_id] = datetime.now()
        self.finish(error_code)

    def get_next_weighted_path(self) -> list[Edge]:
        weight_by_map_id: dict[int, float] = {}
        for map_id in self.map_ids:
            weight_by_map_id[map_id] = self.get_weight_map_id(map_id)
        draw_weight_on_map(weight_by_map_id, self.world_signals)
        path = self.weighted_path.get_best_path(
            self.game_state.player.curr_vertex,
            visited_vertice_uid=set(),
            weight_by_map_id=weight_by_map_id,
            current_path=[],
        )[0]
        if len(path) == 0:
            raise UnexpectedStateException("Did not found any path")
        return path

    def get_weight_map_id(self, map_id: int) -> float:
        last_visited = LAST_VISITED_BY_MAP_ID.get(map_id, MIN_DATE)
        return (
            min((datetime.now() - last_visited).total_seconds(), 1800)
        ) * self.additional_weight_by_map_id.get(map_id, 1)


if __name__ == "__main__":
    last_visited = MIN_DATE
    sleep(1)
    temp = (datetime.now() - last_visited).total_seconds()
    print(temp)
