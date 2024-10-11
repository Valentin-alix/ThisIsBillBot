from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from models.world_graph import Edge, Transition
from protos.game.gamemap_pb2 import MapCurrentEvent, MapComplementaryInformationEvent
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import (
    InteractiveBehavior,
    InteractiveError,
)
from src.core.behaviors.movements.map_change_behavior import (
    MapChangeBehavior,
    MapChangeError,
)
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.edge import (
    get_valid_transition,
    FORBIDDEN_EDGE_TRANSITION,
)
from src.exceptions import UnhandledErrorCodeException, UnexpectedStateException
from src.interfaces.enums.transition_type import TransitionTypeEnum


class EdgeError(StrEnum):
    INVALID_TRANSITION = auto()
    WAS_ATTACKED = auto()


@dataclass
class EdgeBehavior(Behavior):
    interactive_behavior: InteractiveBehavior
    map_move_behavior: MapMoveBehavior
    map_change_behavior: MapChangeBehavior
    path_finding: Pathfinding

    def run(self, edge: Edge) -> None:
        self.logger.info(f"Go to edge: {edge}")
        if edge.m_to.m_mapId == self.game_state.map.map_id:
            raise UnexpectedStateException(f"Already on edge to map id {edge}")

        if edge.m_from.m_mapId != self.game_state.map.map_id:
            raise UnexpectedStateException(
                f"edge from map id {edge.m_from.m_mapId} is not current map id : {self.game_state.map.map_id}"
            )

        self.event_manager.on(
            MapCurrentEvent,
            partial(self.on_map_current_event, expected_map_id=edge.m_to.m_mapId),
            originator=self,
        )

        transition = get_valid_transition(edge, edge.m_transitions, self.game_state)
        if transition is None:
            return self.finish(EdgeError.INVALID_TRANSITION)

        transition_type = transition.m_type
        self.logger.info(f"using transition {transition}")
        if transition_type == TransitionTypeEnum.INTERACTIVE:
            self.use_interactive_transition(edge, transition)
        elif transition_type in [
            TransitionTypeEnum.SCROLL_ACTION,
            TransitionTypeEnum.SCROLL,
            TransitionTypeEnum.MAP_ACTION,
        ]:
            self.use_map_change_transition(edge, transition)
        else:
            self.handle_invalid_transition(edge, transition)

    def on_map_current_event(self, msg: MapCurrentEvent, expected_map_id: int):
        if msg.map_id != expected_map_id:
            if self.game_state.fight.in_fight:
                return self.finish(EdgeError.WAS_ATTACKED)
            raise UnexpectedStateException(
                f"Unexpected map id {msg.map_id} was expecting {expected_map_id}"
            )
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            once=True,
            originator=self,
        )

    def on_map_complementary_information_event(
        self, msg: MapComplementaryInformationEvent
    ):
        return self.finish()

    def use_interactive_transition(self, edge: Edge, transition: Transition):
        interactive_element = self.game_state.interactive.interactive_element_by_id.get(
            transition.m_id
        )
        if interactive_element is None:
            self.logger.warning(
                f"Interactive not found : {transition.m_id}, recalculating path"
            )
            return self.handle_invalid_transition(edge, transition)

        related_skill_uid = next(
            (
                skill.skill_instance_uid
                for skill in interactive_element.enabled_skills
                if skill.skill_id == transition.m_skillId
            ),
            None,
        )
        if related_skill_uid is None:
            self.logger.warning(
                f"related skill uid not found : {interactive_element}, recalculating path"
            )
            return self.handle_invalid_transition(edge, transition)

        move_path_interactive = self.path_finding.get_interactive_near_path(
            player_mp=self.game_state.player.map_point,
            element_mp=MapPoint.from_cell_id(transition.m_cellId),
            skill_ids=[skill.skill_id for skill in interactive_element.enabled_skills],
        )
        if move_path_interactive is None:
            self.logger.warning(
                f"no path found to interactive on {transition.m_cellId} at map {self.game_state.map.map_id} with "
                f"element {interactive_element.element_id}"
            )
            return self.handle_invalid_transition(edge, transition)

        self.interactive_behavior.start(
            callback=None,
            parent=self,
            move_path=move_path_interactive,
            element_id=interactive_element.element_id,
            skill_instance_uid=related_skill_uid,
        )

    def on_interactive_behavior_finished(self, error_code: str | None):
        if error_code is not None and error_code not in [InteractiveError.USE_ERROR]:
            raise UnhandledErrorCodeException(error_code)

    def use_map_change_transition(self, edge: Edge, transition: Transition):
        move_path = self.path_finding.find_path(
            self.game_state.player.map_point,
            {MapPoint.from_cell_id(transition.m_cellId)},
        )
        if move_path.end.cell_id != transition.m_cellId:
            self.logger.info(
                f"move path : {move_path} not ending at transition {transition}, invalid."
            )
            return self.handle_invalid_transition(edge, transition)

        self.map_move_behavior.start(
            callback=partial(
                self.on_map_move_behavior_finished,
                transition_map_id=transition.m_transitionMapId,
                edge=edge,
            ),
            parent=self,
            move_path=move_path,
        )

    def on_map_move_behavior_finished(
        self, error_code: str | None, transition_map_id: int, edge: Edge
    ):
        if error_code is not None and error_code not in [
            MapMoveError.REFUSED,
            MapMoveError.CANCELED_MOVEMENT,
        ]:
            raise UnhandledErrorCodeException(error_code)

        self.map_change_behavior.start(
            callback=partial(self.on_map_change_behavior_finished, edge=edge),
            parent=self,
            map_id=transition_map_id,
            expected_map_id=edge.m_to.m_mapId,
        )

    def on_map_change_behavior_finished(self, error_code: str | None, edge: Edge):
        if error_code is not None and error_code not in [
            MapMoveError.REFUSED,
            MapChangeError.UNEXPECTED_NEW_MAP,
        ]:
            raise UnhandledErrorCodeException(error_code)

    def handle_invalid_transition(self, edge: Edge, transition: Transition):
        FORBIDDEN_EDGE_TRANSITION.add((edge.m_from.m_uid, edge.m_to.m_uid, transition))
        return self.finish(EdgeError.INVALID_TRANSITION)
