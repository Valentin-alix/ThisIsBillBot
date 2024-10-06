from dataclasses import dataclass, field
from enum import StrEnum, auto

from db_dofus_unity.protos.game.gamemap_pb2 import MapComplementaryInformationEvent
from src.common.logger import Logger
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.map_change_behavior import MapChangeBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.world.edge import FORBIDDEN_TRANSITION_IDS
from src.core.logic.world.transition_type import TransitionTypeEnum
from src.core.logic.world.world_path_finder import WorldPathFinder
from src.core.repositories.map_reader import MapReader
from src.core.repositories.world_graph_reader import Edge
from src.core.states.interactive_state import InteractiveState
from src.core.states.player_state import PlayerState


class AutoTripErrorCode(StrEnum):
    PATH_NOT_FOUND = auto()
    INVALID_TRANSITION = auto()


@dataclass
class AutoTripBehavior(Behavior):
    map_move_behavior: MapMoveBehavior
    map_change_behavior: MapChangeBehavior
    interactive_behavior: InteractiveBehavior
    interactive_state: InteractiveState
    player_state: PlayerState
    world_path_finder: WorldPathFinder

    _auto_trip_edges: list[Edge] | None = field(default=None, init=False)
    _target_map_ids: set[int] | None = None

    def run(self, dst: set[int] | Edge):
        if isinstance(dst, set):
            Logger().info(f"Auto trip to map id : {dst}")
            self._target_map_ids = dst
            path = self.world_path_finder.find_path(self.player_state.curr_vertex, dst)
            if path is None:
                return self.finish(AutoTripErrorCode.PATH_NOT_FOUND)
            if len(path) == 0:
                return self.finish()
            self._auto_trip_edges = path
        else:
            Logger().info(f"Auto trip to edge: {dst}")
            self._target_map_ids = None
            self._auto_trip_edges = [dst]

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
            {MapPoint.from_cell_id(transition.m_cellId)},
        )
        if transition_type == TransitionTypeEnum.INTERACTIVE:
            interactive_element = self.interactive_state.interactive_element_by_id.get(
                transition.m_id
            )
            if interactive_element is None:
                Logger().warning(
                    f"Interactive not found : {transition.m_id}, recalculating path"
                )
                FORBIDDEN_TRANSITION_IDS.add(transition.m_id)
                if self._target_map_ids is None:
                    return self.finish(AutoTripErrorCode.INVALID_TRANSITION)
                return self.run(dst=self._target_map_ids)

            related_skill_uid = next(
                (
                    skill.skill_instance_uid
                    for skill in interactive_element.enabled_skills
                    if skill.skill_id == transition.m_skillId
                ),
                None,
            )
            if related_skill_uid is None:
                Logger().warning(
                    f"related skill uid not found : {interactive_element}, recalculating path"
                )
                FORBIDDEN_TRANSITION_IDS.add(transition.m_id)
                if self._target_map_ids is None:
                    return self.finish(AutoTripErrorCode.INVALID_TRANSITION)
                return self.run(dst=self._target_map_ids)

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
                element_id=interactive_element.element_id,
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
                callback=lambda _: self.map_change_behavior.start(
                    callback=lambda _: self.process_edge(),
                    parent=self,
                    map_id=edge.m_transitions.Array[0].m_transitionMapId,
                ),
                parent=self,
                move_path=move_path,
            )
        elif transition_type == TransitionTypeEnum.MAP_ACTION:
            self.map_move_behavior.start(
                callback=lambda _: self.map_change_behavior.start(
                    callback=lambda _: self.process_edge(),
                    parent=self,
                    map_id=edge.m_transitions.Array[0].m_transitionMapId,
                ),
                parent=self,
                move_path=move_path,
            )
        else:
            Logger().warning(f"Unknown transition : {transition_type}")
            return self.finish(AutoTripErrorCode.INVALID_TRANSITION)
