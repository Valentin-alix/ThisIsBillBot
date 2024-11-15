import random
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from threading import Lock
from typing import Callable

from d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from data_center.data_reader import DataReader
from models.world_graph import Edge

from src.const import MIN_DATE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.movements.edge_behavior import EdgeBehavior
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.logic.farms.weights.weight_items import (
    draw_weight_on_map,
)
from src.core.logic.farms.weights.weighted_path import WeightedPath
from src.core.logic.world.edge import draw_edge_path
from src.signals.world_signals import WorldSignals

PATH_LOCK = Lock()
LAST_VISITED_BY_MAP_ID: dict[int, datetime] = {}
EDGE_PATH_BY_CHARACTER_ID: dict[int, list[Edge]] = {}


@dataclass
class RandomFarmBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    edge_behavior: EdgeBehavior
    weighted_path: WeightedPath
    world_signals: WorldSignals
    additional_weight_by_map_id: dict[int, float] = field(
        default_factory=dict, init=False
    )
    get_additional_weight_by_map_id: Callable[[int], float] = field(
        init=False, default=lambda _: 0
    )
    map_ids: set[int] = field(default_factory=set, init=False)
    _edge_path: list[Edge] | None = field(default=None, init=False)

    @property
    def edge_path(self):
        return self._edge_path

    @edge_path.setter
    def edge_path(self, value: list[Edge] | None):
        self._edge_path = value
        if value is None:
            EDGE_PATH_BY_CHARACTER_ID.pop(self.game_state.player.character_id, None)
        else:
            EDGE_PATH_BY_CHARACTER_ID[self.game_state.player.character_id] = value

    def init_random_farm(
        self,
        area_id: int | None,
        sub_area_id: int | None,
        get_additional_weight_by_map_id: Callable[[int], float],
    ):
        self.get_additional_weight_by_map_id = get_additional_weight_by_map_id
        self.additional_weight_by_map_id.clear()
        self.edge_path = None
        self.world_signals.reset_weight.emit()
        self.map_ids = self.get_map_ids(area_id, sub_area_id)

    def stop(self) -> None:
        self.edge_path = None
        return super().stop()

    def run(
        self,
    ):
        if (
            (self.edge_path is None or len(self.edge_path) == 0)
            and self.game_state.map.map_id not in self.map_ids
        ) or (
            self.edge_path is not None
            and len(self.edge_path) > 0
            and self.edge_path[0].m_from.m_mapId != self.game_state.map.map_id
        ):
            self.edge_path = None
            self.logger.info("go to area for farm")
            return self.auto_trip_smart_behavior.start(
                callback=self.on_auto_trip_world_behavior_finished,
                parent=self,
                map_ids=self.map_ids,
            )

        if self.edge_path is None or len(self.edge_path) == 0:
            self.logger.info("Empty edge path, recalculating")
            with PATH_LOCK:
                self.edge_path = None
                self.edge_path = self.get_next_weighted_path()
            if self.edge_path is None:
                return self.auto_trip_smart_behavior.start(
                    callback=self.on_auto_trip_world_behavior_finished,
                    parent=self,
                    map_ids=self.map_ids - {self.game_state.map.map_id},
                )
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
            self.logger.info(
                f"setting map id based on {area_id}, ignore sub area with too high level"
            )
            map_ids: set[int] = set()
            for sub_area_id in DataReader().sub_areas_by_area_id[area_id]:
                if DataReader().sub_area_by_id[sub_area_id].level > (
                    self.game_state.player.level + 40
                ):
                    continue
                map_ids |= set(DataReader().sub_area_by_id[sub_area_id].mapIds)
            return map_ids
        return set(DataReader().sub_area_by_id[self.game_state.map.sub_area_id].mapIds)

    def on_edge_behavior_finished(self, error_code: str | None, edge: Edge):
        if self.edge_path is None:
            raise ValueError("edge path should not be none")
        if error_code is not None:
            self.edge_path = None
            if error_code is not MapChangeError.UNEXPECTED_NEW_MAP:
                return self.finish(error_code)
        else:
            self.edge_path.remove(edge)
        LAST_VISITED_BY_MAP_ID[self.game_state.map.map_id] = datetime.now()
        self.event_manager.on(
            MapComplementaryInformationEvent,
            partial(
                self.on_map_complementary_information_event_after_edge,
                error_code=error_code,
            ),
            originator=self,
            once=True,
        )

    def on_map_complementary_information_event_after_edge(
        self, msg: MapComplementaryInformationEvent, error_code: str | None
    ):
        self.finish(error_code)

    def on_auto_trip_world_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            self.logger.error(error_code)
            return self.finish(error_code)
        LAST_VISITED_BY_MAP_ID[self.game_state.map.map_id] = datetime.now()
        self.finish(error_code)

    def get_next_weighted_path(self) -> list[Edge] | None:
        cached_weight_by_map_id: dict[int, float] = {}
        path = self.weighted_path.monte_carlo_path(
            start_vertex=self.game_state.player.curr_vertex,
            get_weight_by_edge_func=self.get_weight_edge,
            weight_by_map_id=cached_weight_by_map_id,
            count_map_in_area=len(self.map_ids),
        )[0]
        draw_weight_on_map(cached_weight_by_map_id, self.world_signals)
        if len(path) == 0:
            self.logger.warning("Did not found any path")
            return None

        return path

    def get_weight_edge(self, edge: Edge) -> float:
        if edge.m_to.m_mapId not in self.map_ids:
            return -1
        last_visited = LAST_VISITED_BY_MAP_ID.get(edge.m_to.m_mapId, MIN_DATE)
        if (
            additional_weight_map := self.additional_weight_by_map_id.get(
                edge.m_to.m_mapId
            )
        ) is None:
            additional_weight_map = self.get_additional_weight_by_map_id(
                edge.m_to.m_mapId
            )
            self.additional_weight_by_map_id[edge.m_to.m_mapId] = additional_weight_map

        count_edge_already_on_other_players = len(
            [
                edge
                for character_id, edge_path in list(EDGE_PATH_BY_CHARACTER_ID.items())
                for edge in edge_path
                if character_id != self.game_state.player.character_id and edge == edge
            ]
        )

        return (
            (min((datetime.now() - last_visited).total_seconds(), 3600) ** 3)
            * (1 + additional_weight_map)
            * random.uniform(0.65, 1)
        ) / (1 + count_edge_already_on_other_players)
