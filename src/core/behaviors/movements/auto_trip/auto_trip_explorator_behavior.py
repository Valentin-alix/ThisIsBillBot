from dataclasses import dataclass
from functools import partial

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_zaap_behavior import (
    AutoTripZaapBehavior,
)
from src.core.data_center.data_reader import DataReader
from src.core.logic.world.map_position import get_dist_to_maps
from src.core.logic.world.waypoint import get_near_waypoint
from src.exceptions import UnhandledErrorCodeException


@dataclass
class AutoTripExploratorBehavior(Behavior):
    """auto trip with zaap, discover new zaap if needed"""

    auto_trip_zaap_behavior: AutoTripZaapBehavior

    def run(self, map_ids: set[int]) -> None:
        if not self.game_state.player.is_sub or True:
            return self.on_explored_near_zaap(map_ids=map_ids)
        ends_pos = [DataReader().map_pos_by_map_id[map_id] for map_id in map_ids]
        dist_player_to_ends = get_dist_to_maps(self.game_state.map.map_pos, ends_pos)
        # discover near waypoint & go dst
        near_waypoint = get_near_waypoint(
            available_waypoint_map_ids=self.game_state.player.waypoint_map_ids,
            dist_player_to_ends=dist_player_to_ends,
            ends_pos=ends_pos,
            check_owned=False,
        )
        if (
            near_waypoint
            and near_waypoint.map_id not in self.game_state.player.waypoint_map_ids
        ):
            self.logger.info(f"let's discover new zaap first : {near_waypoint.map_id}")
            return self.auto_trip_zaap_behavior.start(
                map_ids={near_waypoint.map_id},
                callback=partial(
                    self.on_auto_trip_zaap_behavior_finished, map_ids=map_ids
                ),
                parent=self,
            )
        self.on_explored_near_zaap(map_ids=map_ids)

    def on_auto_trip_zaap_behavior_finished(
        self, error_code: str | None, map_ids: set[int]
    ):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.on_explored_near_zaap(map_ids)

    def on_explored_near_zaap(self, map_ids: set[int]):
        self.auto_trip_zaap_behavior.start(
            map_ids=map_ids, callback=self.finish, parent=self
        )
