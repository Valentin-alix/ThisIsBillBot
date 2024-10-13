from dataclasses import dataclass

from d3_mapping.resources.protos.game.character_pb2 import (
    CharacterLifeStatusEvent,
    FreeSoulRequest,
)
from d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapTeleportOnSameEvent,
)
from src.const import ON_NEW_MAP_BEFORE_ACTION
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import AutoTripBehavior
from data_center.map_reader import MapReader
from data_center.world_graph_reader import WorldGraphReader
from grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.astar_no_interactive import AstarNoInteractive
from src.exceptions import UnhandledErrorCodeException, UnexpectedStateException
from src.interfaces.enums.skill_enum import SkillEnum


@dataclass
class ReviveBehavior(Behavior):
    auto_trip_behavior: AutoTripBehavior
    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding
    astar_no_interactive: AstarNoInteractive

    def run(self) -> None:
        if (
            self.game_state.player.life_state
            != CharacterLifeStatusEvent.LifeStatus.TOMBSTONE
        ):
            return self.finish()

        self.run_timer(ON_NEW_MAP_BEFORE_ACTION, self.free_soul)

    def free_soul(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            originator=self,
            once=True,
        )
        self.event_manager.on(
            MapTeleportOnSameEvent,
            self.on_map_teleport_on_same_event,
            originator=self,
            once=True,
        )
        req = FreeSoulRequest()
        self.event_manager.send(req)

    def on_map_teleport_on_same_event(self, msg: MapTeleportOnSameEvent):
        self.event_manager.clear_listener_by_origin_and_type(
            MapComplementaryInformationEvent, self
        )
        self.go_to_phenix_and_revive()

    def on_map_complementary_information_event(
        self, msg: MapComplementaryInformationEvent
    ):
        self.go_to_phenix_and_revive()

    def go_to_phenix_and_revive(self):
        dst_vertexes = WorldGraphReader().get_vertexes(
            self.game_state.map.phoenix_map_id
        )
        path_to_phoenix_map = self.astar_no_interactive.find_path(
            self.game_state.player.curr_vertex, dst_vertexes
        )
        if path_to_phoenix_map is None:
            raise UnexpectedStateException(
                f"path to phoenix at {self.game_state.map.phoenix_map_id} is none"
            )
        self.auto_trip_behavior.start(
            edge_path=path_to_phoenix_map,
            callback=self.on_auto_trip_behavior_finished,
            parent=self,
        )

    def on_auto_trip_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        phoenix_element = next(
            element
            for element in self.game_state.interactive.interactive_element_by_id.values()
            if len(element.enabled_skills) > 0
            and element.enabled_skills[0].skill_id == SkillEnum.PHOENIX
        )
        ref_data = MapReader().get_ref_data_by_element_id(self.game_state.map.map_id)[
            phoenix_element.element_id
        ]
        move_path = self.path_finding.get_interactive_near_path(
            self.game_state.player.map_point,
            MapPoint.from_cell_id(ref_data.cellId),
            [skill.skill_id for skill in phoenix_element.enabled_skills],
        )
        self.interactive_behavior.start(
            move_path=move_path,
            element_id=phoenix_element.element_id,
            skill_instance_uid=phoenix_element.enabled_skills[0].skill_instance_uid,
            callback=self.on_phoenix_used,
            parent=self,
        )

    def on_phoenix_used(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.event_manager.on(
            CharacterLifeStatusEvent, lambda _: self.finish(), originator=self
        )
