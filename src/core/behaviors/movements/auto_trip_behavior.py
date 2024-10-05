from dataclasses import dataclass, field

from db_dofus_unity.protos.game.gamemap_pb2 import MapComplementaryInformationEvent
from src.common.logger import Logger
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.map_change_behavior import MapChangeBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.world.transition_type import TransitionTypeEnum
from src.core.logic.world.world_path_finder import WorldPathFinder
from src.core.repositories.map_reader import MapReader
from src.core.repositories.world_graph_reader import Edge
from src.core.states.interactive_state import InteractiveState
from src.core.states.player_state import PlayerState


@dataclass
class AutoTripBehavior(Behavior):
    map_move_behavior: MapMoveBehavior
    map_change_behavior: MapChangeBehavior
    interactive_behavior: InteractiveBehavior
    interactive_state: InteractiveState
    player_state: PlayerState
    world_path_finder: WorldPathFinder

    _auto_trip_edges: list[Edge] | None = field(default=None, init=False)

    def run(self, map_id: int):
        path = self.world_path_finder.find_path(map_id)
        if path is None:
            return self.finish()
        if len(path) == 0:
            return self.finish()

        self._auto_trip_edges = path
        self.process_edge()

    def process_edge(self):
        if self._auto_trip_edges is None or len(self._auto_trip_edges) == 0:
            return self.finish()

        edge = self._auto_trip_edges.pop(0)
        Logger().info(f"Current edge : {edge}")
        transition = edge.m_transitions.Array[0]
        transition_type = transition.m_type

        Logger().info(f"finding path to {transition.m_cellId}")
        move_path = self.map_move_behavior.path_finding.find_path(
            self.player_state.map_point,
            MapPoint.from_cell_id(transition.m_cellId),
        )
        if transition_type == TransitionTypeEnum.INTERACTIVE:
            interactive_element = self.interactive_state.interactive_elements_by_id[
                transition.m_id
            ]
            related_skill_uid = next(
                skill.skill_instance_uid
                for skill in interactive_element.interactive_element.enabled_skills
                if skill.skill_id == transition.m_skillId
            )
            self.event_manager.on(
                MapComplementaryInformationEvent,
                lambda _: self.process_edge(),
                once=True,
                originator=self,
            )
            self.interactive_behavior.start(
                callback=None,
                parent=self,
                move_path=move_path,
                element_id=interactive_element.interactive_element.element_id,
                skill_instance_uid=related_skill_uid,
            )

        elif transition_type in [
            TransitionTypeEnum.SCROLL_ACTION,
            TransitionTypeEnum.SCROLL,
        ]:
            Logger().info(transition.m_cellId)
            Logger().info(
                MapReader().get_cell_data_by_cell_id(
                    edge.m_from.m_mapId, transition.m_cellId
                )
            )
            self.map_move_behavior.start(
                callback=lambda: self.map_change_behavior.start(
                    callback=self.process_edge,
                    parent=self,
                    map_id=edge.m_transitions.Array[0].m_transitionMapId,
                ),
                parent=self,
                move_path=move_path,
            )
        elif transition_type == TransitionTypeEnum.MAP_ACTION:
            self.map_move_behavior.start(
                callback=lambda: self.map_change_behavior.start(
                    callback=self.process_edge,
                    parent=self,
                    map_id=edge.m_transitions.Array[0].m_transitionMapId,
                ),
                parent=self,
                move_path=move_path,
            )
        else:
            Logger().warning(f"Unknown transition : {transition_type}")
