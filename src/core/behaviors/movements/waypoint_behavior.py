from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from datas.protos.non_obf.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from datas.protos.non_obf.game.haven_bag_pb2 import (
    HavenBagEnterRequest,
    HavenBagExitRequest,
)
from datas.protos.non_obf.game.teleportation_pb2 import (
    Teleporter,
    TeleportRequest,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from dofus_unity_reader.game_constants.element_type import ElementTypeEnum
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.world_graph import Vertice

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import (
    AutoTripBehavior,
)
from src.core.config import BASE_RANGE
from src.core.engine.movements.map.map_position_flags import allow_teleport_to
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.engine.movements.world.astar_allow_capability import (
    AstarAllowHavreSac,
)
from src.exceptions import UnexpectedStateException


class WaypointErrorCode(StrEnum):
    UNREACHABLE_HAVRE_MAP = auto()


@dataclass
class WaypointBehavior(Behavior):
    interactive_behavior: InteractiveBehavior
    astar_allow_havre_sac: AstarAllowHavreSac
    auto_trip_behavior: AutoTripBehavior
    pathfinding: Pathfinding

    def run(self, map_id: int, dst_map_ids: set[int]) -> None:
        if self.game_state.map.is_in_haven_bag:
            return self.go_and_use_waypoint(map_id)
        map_data = DataReader().map_pos_by_map_id[self.game_state.map.map_id]
        self.event_manager.prevent(HavenBagEnterRequest, originator=self)
        if not allow_teleport_to(map_data.m_flags):
            dst_vertex: set[Vertice] = {
                vertex
                for dst in dst_map_ids
                for vertex in WorldGraphReader().get_vertexes(dst)
            }
            self.astar_allow_havre_sac.set_context(
                self.game_state.get_world_path_context()
            )
            path = self.astar_allow_havre_sac.find_path(
                start=self.game_state.map.curr_vertex,
                ends=dst_vertex,
            )
            if path is None:
                return self.finish(WaypointErrorCode.UNREACHABLE_HAVRE_MAP)

            return self.auto_trip_behavior.start(
                edge_path=path,
                callback=partial(self.on_auto_trip_behavior_finished, map_id=map_id),
                parent=self,
            )
        self.on_map_allowing_havre_sac(map_id)

    def on_auto_trip_behavior_finished(self, error_code: str | None, map_id: int):
        self.raise_if_error(error_code)
        self.on_map_allowing_havre_sac(map_id)

    def on_map_allowing_havre_sac(self, map_id: int):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            callback=partial(self.on_entered_havre_sac, map_id=map_id),
            originator=self,
            once=True,
        )
        req = HavenBagEnterRequest(owner=self.game_state.player.character_id)
        self.event_manager.send(req)

    def on_entered_havre_sac(self, msg: MapComplementaryInformationEvent, map_id: int):
        if not msg.HasField("haven_bag_information"):
            return self.finish(WaypointErrorCode.UNREACHABLE_HAVRE_MAP)
        self.go_and_use_waypoint(map_id)

    def go_and_use_waypoint(self, map_id: int):
        zaap = next(
            (
                element
                for element in self.game_state.interactive.interactive_element_by_id.values()
                if element.element_type_id == ElementTypeEnum.ZAAP
            ),
            None,
        )
        if zaap is None:
            raise UnexpectedStateException("Did not found any zaap inside havre sac.")

        if len(zaap.enabled_skills) == 0:
            self.event_manager.on(
                MapComplementaryInformationEvent,
                lambda _: self.finish(WaypointErrorCode.UNREACHABLE_HAVRE_MAP),
                once=True,
                originator=self,
            )
            return self.send_message_delayed(HavenBagExitRequest(), BASE_RANGE)

        mp_zaap = MapPoint.from_cell_id(
            self.game_state.interactive.stated_element_by_id[zaap.element_id][0].cell_id
        )
        move_path = self.pathfinding.find_path(
            self.game_state.get_map_movement_context(),
            self.game_state.map.map_point,
            {mp_zaap},
        )
        self.run_timer(
            BASE_RANGE,
            lambda: self.interactive_behavior.start(
                parent=self,
                callback=partial(self.on_zaap_used, map_id=map_id),
                move_path=move_path,
                element_id=zaap.element_id,
                skill_instance_uid=zaap.enabled_skills[0].skill_instance_uid,
            ),
        )

    def on_zaap_used(self, error_code: str | None, map_id: int):
        self.raise_if_error(error_code)

        self.event_manager.on(
            MapComplementaryInformationEvent,
            callback=partial(
                self.on_map_complementary_information_event, map_id=map_id
            ),
            originator=self,
            once=True,
        )
        req = TeleportRequest(
            source_type=Teleporter.TELEPORTER_HAVEN_BAG, map_id=map_id
        )
        self.send_message_delayed(req, BASE_RANGE)

    def on_map_complementary_information_event(
        self, msg: MapComplementaryInformationEvent, map_id: int
    ):
        if msg.map_id == map_id:
            return self.finish()
        raise UnexpectedStateException(
            f"different map id {msg.map_id} after using zaap for map id : {map_id}"
        )
