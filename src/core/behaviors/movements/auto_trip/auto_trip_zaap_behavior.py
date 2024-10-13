from dataclasses import dataclass
from functools import partial

from models.datas.map_positions_root import MapPositionsRootItem
from d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from d3_mapping.resources.protos.game.haven_bag_pb2 import HavenBagExitRequest
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import (
    AutoTripBehavior,
    AutoTripErrorCode,
)
from src.core.behaviors.movements.waypoint_behavior import (
    WaypointBehavior,
    WaypointErrorCode,
)
from data_center.data_reader import DataReader
from src.core.logic.world.map_position import get_dist_to_maps
from src.core.logic.world.waypoint import get_near_waypoint
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.enums.area_enum import AreaEnum


@dataclass
class AutoTripZaapBehavior(Behavior):
    """auto trip with zaap"""

    auto_trip_behavior: AutoTripBehavior
    waypoint_behavior: WaypointBehavior

    def run(self, map_ids: set[int]) -> None:
        if (
            not self.game_state.player.is_sub
            or self.game_state.player.level < 10
            or DataReader().sub_area_by_id[self.game_state.map.sub_area_id].areaId
            == AreaEnum.INCARNAM
            or self.game_state.inventory.kamas < 10_000
        ):
            self.logger.info("Can't use zaap, walk to dst")
            return self.auto_trip_behavior.start(
                callback=self.finish, parent=self, map_ids=map_ids
            )

        dst_map_pos = [DataReader().map_pos_by_map_id[map_id] for map_id in map_ids]
        dist_player_to_ends = get_dist_to_maps(self.game_state.map.map_pos, dst_map_pos)

        self.logger.info(
            f"Get near waypoint with dist player to ends : {dist_player_to_ends} with waypoints : {self.game_state.player.waypoint_map_ids}"
        )
        near_waypoint = get_near_waypoint(
            self.game_state.player.waypoint_map_ids,
            dist_player_to_ends,
            dst_map_pos,
            True,
        )
        if near_waypoint is not None:
            return self.waypoint_behavior.start(
                callback=partial(
                    self.on_near_waypoint_behavior_finished,
                    map_ids=map_ids,
                    ends_pos=dst_map_pos,
                ),
                parent=self,
                map_id=near_waypoint.map_id,
                dst_map_ids=map_ids,
            )
        if self.game_state.map.is_in_haven_bag:
            self.event_manager.on(
                MapComplementaryInformationEvent,
                lambda _: self.walk_to_map_ids(map_ids=map_ids, ends_pos=dst_map_pos),
                originator=self,
                once=True,
            )
            req = HavenBagExitRequest()
            self.event_manager.send(req)
        else:
            self.walk_to_map_ids(map_ids=map_ids, ends_pos=dst_map_pos)

    def on_near_waypoint_behavior_finished(
        self,
        error_code: str | None,
        map_ids: set[int],
        ends_pos: list[MapPositionsRootItem],
    ):
        if error_code is WaypointErrorCode.UNREACHABLE_HAVRE_MAP:
            self.walk_to_map_ids(map_ids, ends_pos)
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.walk_to_map_ids(map_ids, ends_pos)

    def walk_to_map_ids(self, map_ids: set[int], ends_pos: list[MapPositionsRootItem]):
        self.auto_trip_behavior.start(
            parent=self,
            map_ids=map_ids,
            callback=partial(
                self.on_auto_trip_behavior_finished, map_ids=map_ids, ends_pos=ends_pos
            ),
        )

    def on_auto_trip_behavior_finished(
        self,
        error_code: str | None,
        map_ids: set[int],
        ends_pos: list[MapPositionsRootItem],
    ):
        if error_code is AutoTripErrorCode.PATH_NOT_FOUND:
            self.logger.info("Path not found, try to use waypoint")
            near_waypoint = get_near_waypoint(
                self.game_state.player.waypoint_map_ids, None, ends_pos, True
            )
            if near_waypoint is None:
                return self.finish(AutoTripErrorCode.PATH_NOT_FOUND)
            return self.waypoint_behavior.start(
                callback=partial(
                    self.on_waypoint_behavior_finished_after_auto_trip_fail,
                    map_ids=map_ids,
                ),
                parent=self,
                map_id=near_waypoint.map_id,
                dst_map_ids=map_ids,
            )
        self.finish(error_code)

    def on_waypoint_behavior_finished_after_auto_trip_fail(
        self, error_code: str | None, map_ids: set[int]
    ):
        if error_code is WaypointErrorCode.UNREACHABLE_HAVRE_MAP:
            return self.finish(AutoTripErrorCode.PATH_NOT_FOUND)
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.auto_trip_behavior.start(
            parent=self, map_ids=map_ids, callback=self.finish
        )
