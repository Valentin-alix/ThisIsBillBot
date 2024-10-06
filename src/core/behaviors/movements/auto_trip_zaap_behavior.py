from dataclasses import dataclass
from typing import Callable

from db_dofus_unity.gen.gen_datas import MapPositionsRoot
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip_behavior import AutoTripBehavior
from src.core.behaviors.movements.waypoint_behavior import WaypointBehavior
from src.core.repositories.data_reader import DataReader
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.interfaces.enums.data_enum import DataEnum
from src.interfaces.enums.world import WorldEnum

type WaypointInfo = tuple[int, MapPositionsRoot.Data, float]


@dataclass
class AutoTripZaapBehavior(Behavior):
    player_state: PlayerState
    auto_trip_behavior: AutoTripBehavior
    waypoint_behavior: WaypointBehavior
    map_state: MapState

    def run(self, dst: set[int]) -> None:
        if (
            not self.player_state.is_sub
            or self.player_state.level < 10
            or DataReader().sub_area_by_id[self.map_state.sub_area_id].areaId
            == DataEnum.AREA_INCARNAM
        ):
            return self.auto_trip_behavior.start(
                callback=self.finish, parent=self, dst=dst
            )

        # discover near waypoint & go dst
        near_waypoint = self.get_near_waypoint(dst, check_owned=False)
        if (
            near_waypoint is not None
            and (
                self.get_dist_to_ends(self.map_state.map_pos, [near_waypoint[1]])
                > near_waypoint[2]
            )
            and not near_waypoint[0] in self.player_state.waypoint_ids
        ):
            return self.go_to_map_ids(
                dst={near_waypoint[1].id},
                callback=lambda _: self.auto_trip_behavior.start(
                    callback=self.finish, parent=self, dst=dst
                ),
            )
        self.go_to_map_ids(
            dst=dst,
            callback=self.finish,
        )

    def go_to_map_ids(self, dst: set[int], callback: Callable[[str], None]):
        near_waypoint = self.get_near_waypoint(dst, True)
        if near_waypoint is not None and (
            self.get_dist_to_ends(self.map_state.map_pos, [near_waypoint[1]])
            > near_waypoint[2]
        ):
            return self.waypoint_behavior.start(
                callback=lambda _: self.auto_trip_behavior.start(
                    callback=callback, parent=self, dst=dst
                ),
                parent=self,
                map_id=near_waypoint[0],
            )
        self.auto_trip_behavior.start(callback=callback, parent=self, dst=dst)

    def get_near_waypoint(self, dst: set[int], check_owned: bool):
        near_waypoint: WaypointInfo | None = None

        ends_pos = [DataReader().map_pos_by_map_id[map_id] for map_id in dst]
        for waypoint in DataReader().waypoint_by_id.values():
            if waypoint.activated == 0:
                continue
            if check_owned and waypoint.mapId not in self.player_state.waypoint_ids:
                continue
            map_waypoint_pos = DataReader().map_pos_by_map_id[waypoint.mapId]
            if map_waypoint_pos.worldMap != WorldEnum.TWELVE:
                continue

            dist_waypoint = self.get_dist_to_ends(map_waypoint_pos, ends_pos)
            if near_waypoint is None or near_waypoint[2] > dist_waypoint:
                near_waypoint = (waypoint.mapId, map_waypoint_pos, dist_waypoint)

        return near_waypoint if near_waypoint else None

    def get_dist_to_ends(
        self, map_pos: MapPositionsRoot.Data, ends_pos: list[MapPositionsRoot.Data]
    ) -> float:
        return min(
            abs(map_pos.posX - end_pos.posX) + abs(map_pos.posY - end_pos.posY)
            for end_pos in ends_pos
        )
