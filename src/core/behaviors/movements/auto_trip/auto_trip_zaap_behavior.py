from dataclasses import dataclass
from functools import partial

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import AutoTripBehavior
from src.core.behaviors.movements.waypoint_behavior import (
    WaypointBehavior,
    WaypointErrorCode,
)
from src.core.data_center.data_reader import DataReader
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
            or self.game_state.inventory.kamas < 10000
        ):
            return self.auto_trip_behavior.start(
                callback=self.finish, parent=self, map_ids=map_ids
            )

        dst_map_pos = [DataReader().map_pos_by_map_id[map_id] for map_id in map_ids]
        dist_player_to_ends = get_dist_to_maps(self.game_state.map.map_pos, dst_map_pos)

        near_waypoint = get_near_waypoint(
            self.game_state.player.waypoint_map_ids,
            dist_player_to_ends,
            dst_map_pos,
            True,
        )
        if near_waypoint is not None:
            return self.waypoint_behavior.start(
                callback=partial(self.on_waypoint_behavior_finished, map_ids=map_ids),
                parent=self,
                map_id=near_waypoint.map_id,
                dst_map_ids=map_ids,
            )
        self.on_waypoint_treated(map_ids=map_ids)

    def on_waypoint_behavior_finished(self, error_code: str | None, map_ids: set[int]):
        if error_code is WaypointErrorCode.UNREACHABLE_HAVRE_MAP:
            self.on_waypoint_treated(map_ids)
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.on_waypoint_treated(map_ids)

    def on_waypoint_treated(self, map_ids: set[int]):
        self.auto_trip_behavior.start(
            parent=self, map_ids=map_ids, callback=self.finish
        )
