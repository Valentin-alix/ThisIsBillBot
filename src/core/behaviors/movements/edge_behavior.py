from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from datas.protos.non_obf.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapCurrentEvent,
)
from dofus_unity_reader.data_center.map_reader import MapReader
from dofus_unity_reader.game_constants.transition_type import TransitionTypeEnum
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.world_graph import Edge, Transition

from src.core.behaviors.behavior import Behavior, BehaviorState
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.interactives.interactive_behavior import (
    InteractiveBehavior,
    InteractiveError,
)
from src.core.behaviors.movements.map_change_behavior import (
    MapChangeBehavior,
    MapChangeError,
)
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.config import BASE_RANGE, BIG_RANGE
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.engine.movements.world.edge import get_valid_transition


class EdgeError(StrEnum):
    NO_VALID_TRANSITION = auto()
    INVALID_STARTING_MAP = auto()


@dataclass
class EdgeBehavior(Behavior):
    interactive_behavior: InteractiveBehavior
    map_move_behavior: MapMoveBehavior
    map_change_behavior: MapChangeBehavior
    path_finding: Pathfinding
    fight_behavior: FightBehavior

    def run(self, edge: Edge) -> None:
        self.clear_behavior()
        self.logger.info(f"Go to edge: {edge}")
        if edge.m_to.m_mapId == self.game_state.map.map_id:
            return self.finish()
        if edge.m_from.m_mapId != self.game_state.map.map_id:
            self.logger.warning(
                f"edge from map id {edge.m_from.m_mapId} is not current map id : {self.game_state.map.map_id},"
                f"probably in transition to map id"
            )
            return self.finish(EdgeError.INVALID_STARTING_MAP)
        transition = get_valid_transition(
            edge, edge.m_transitions, self.game_state.get_world_transition_context()
        )
        if transition is None:
            return self.finish(EdgeError.NO_VALID_TRANSITION)

        self.event_manager.on(
            FightMapInformationEvent,
            partial(self.on_fight_map_information_event, edge=edge),
            originator=self,
        )

        transition_type = transition.m_type
        self.logger.info(f"using transition {transition}")
        if transition_type == TransitionTypeEnum.INTERACTIVE:
            self.use_interactive_transition(edge, transition)
        elif transition_type in [
            TransitionTypeEnum.SCROLL_ACTION,
            TransitionTypeEnum.SCROLL,
        ]:
            self.use_map_change_transition(edge, transition)
        elif transition_type == TransitionTypeEnum.MAP_ACTION:
            self.use_map_action_transition(edge, transition)
        else:
            self.logger.error(f"invalid transition type : {transition_type}")
            self.handle_invalid_transition(edge, transition)
            self.run_timer(BASE_RANGE, lambda: self.run(edge))

    def on_fight_map_information_event(self, msg: FightMapInformationEvent, edge: Edge):
        if self.fight_behavior.state != BehaviorState.STOPPED:
            self.logger.info("FightBehavior is not in state stopped, don't start")
            return
        with self.event_manager.lock:
            self.clear_behavior()
            self.event_manager.on(
                FightMapInformationEvent,
                partial(self.on_fight_map_information_event, edge=edge),
                originator=self,
            )
            self.fight_behavior.start(
                partial(self.on_fight_behavior_finished, edge=edge), parent=self
            )

    def on_fight_behavior_finished(self, edge: Edge, error_code: str | None):
        self.run_timer(BIG_RANGE, lambda: self.run(edge))

    def use_interactive_transition(self, edge: Edge, transition: Transition):
        target_element = (
            self.game_state.interactive.interactive_element_by_id.get(transition.m_id)
            if transition.m_id not in self.game_state.map.excluded_element_ids
            else None
        )
        if target_element is None:
            for elem in self.game_state.interactive.interactive_element_by_id.values():
                if elem.element_id in self.game_state.map.excluded_element_ids:
                    continue
                elem_data = (
                    MapReader()
                    .get_ref_data_by_element_id_by_map_id(edge.m_from.m_mapId)
                    .get(elem.element_id)
                )
                if (
                    elem_data
                    and elem_data.cellId == transition.m_cellId
                    and any(
                        skill.skill_id == transition.m_skillId
                        for skill in elem.enabled_skills
                    )
                ):
                    target_element = elem
                    break

        if target_element is None:
            self.logger.error(
                f"Did not found any potential valid interactive at {transition.m_cellId} for skill {transition.m_skillId}, recalculating path"
            )
            self.handle_invalid_transition(edge, transition)
            return self.run_timer(BASE_RANGE, lambda: self.run(edge))

        related_skill = next(
            (
                skill
                for skill in target_element.enabled_skills
                if skill.skill_id == transition.m_skillId
            ),
            None,
        )
        if related_skill is None:
            self.game_state.map.excluded_element_ids.add(target_element.element_id)
            self.logger.error(f"related skill uid not found : {target_element}")
            return self.run_timer(BASE_RANGE, lambda: self.run(edge))

        move_path_interactive = self.path_finding.get_interactive_near_path(
            context=self.game_state.get_map_movement_context(),
            player_mp=self.game_state.map.map_point,
            element_mp=MapPoint.from_cell_id(transition.m_cellId),
            skill_ids=[related_skill.skill_id],
        )
        if move_path_interactive is None:
            self.game_state.map.excluded_element_ids.add(target_element.element_id)
            self.logger.error(
                f"no path found to interactive on {transition.m_cellId} at map {self.game_state.map.map_id} with "
                f"element {target_element.element_id}"
            )
            return self.run_timer(BASE_RANGE, lambda: self.run(edge))

        self.event_manager.on(
            MapCurrentEvent,
            partial(self.on_map_current_event, expected_map_id=edge.m_to.m_mapId),
            originator=self,
            once=True,
            override_on_self=True,
            timeout=30,
            on_timeout=lambda: self.on_timeout_map_after_interactive(
                edge, target_element.element_id
            ),
        )
        self.interactive_behavior.start(
            callback=partial(
                self.on_interactive_behavior_finished,
                edge=edge,
                transition=transition,
                element_id=target_element.element_id,
            ),
            parent=self,
            move_path=move_path_interactive,
            element_id=target_element.element_id,
            skill_instance_uid=related_skill.skill_instance_uid,
        )

    def on_timeout_map_after_interactive(self, edge: Edge, element_id: int):
        self.game_state.map.excluded_element_ids.add(element_id)
        self.run(edge)

    def on_timeout_map_after_map_action(self, edge: Edge, transition: Transition):
        self.logger.error("Timeout waiting for map change after map action")
        self.handle_invalid_transition(edge, transition)
        self.run_timer(BASE_RANGE, lambda: self.run(edge))

    def on_interactive_behavior_finished(
        self,
        error_code: str | None,
        edge: Edge,
        transition: Transition,
        element_id: int,
    ):
        if error_code is not None:
            if error_code == MapMoveError.REFUSED:
                self.logger.error("map move refused after interactive")
                self.handle_invalid_transition(edge, transition)
                return self.run_timer(BASE_RANGE, lambda: self.run(edge))
            elif error_code == InteractiveError.USE_ERROR:
                self.game_state.map.excluded_element_ids.add(element_id)
                return self.run_timer(BASE_RANGE, lambda: self.run(edge))
            elif error_code in [
                MapMoveError.CANCELED_MOVEMENT,
                MapMoveError.INVALID_STARTING_POINT,
            ]:
                return self.run_timer(BASE_RANGE, lambda: self.run(edge))
            self.raise_if_error(error_code)

    def use_map_action_transition(self, edge: Edge, transition: Transition):
        move_path = self.path_finding.find_path(
            self.game_state.get_map_movement_context(),
            self.game_state.map.map_point,
            {MapPoint.from_cell_id(transition.m_cellId)},
        )
        if move_path.end.cell_id != transition.m_cellId:
            self.logger.error(
                f"move path : {move_path} not ending at transition {transition}, invalid."
            )
            self.handle_invalid_transition(edge, transition)
            return self.run_timer(BASE_RANGE, lambda: self.run(edge))

        self.event_manager.on(
            MapCurrentEvent,
            partial(self.on_map_current_event, expected_map_id=edge.m_to.m_mapId),
            originator=self,
            once=True,
            override_on_self=True,
            timeout=30,
            on_timeout=lambda: self.on_timeout_map_after_map_action(edge, transition),
        )

        self.map_move_behavior.start(
            callback=partial(
                self.on_map_move_behavior_for_map_action_finished,
                edge=edge,
                transition=transition,
            ),
            parent=self,
            move_path=move_path,
        )

    def on_map_move_behavior_for_map_action_finished(
        self, error_code: str | None, edge: Edge, transition: Transition
    ):
        if error_code is not None:
            if error_code in [
                MapMoveError.CANCELED_MOVEMENT,
                MapMoveError.INVALID_STARTING_POINT,
            ]:
                self.logger.warning("Retry edge")
                return self.run_timer(BASE_RANGE, lambda: self.run(edge))
            elif error_code is MapMoveError.REFUSED:
                self.logger.error("map move refused")
                self.handle_invalid_transition(edge, transition)
                return self.run_timer(BASE_RANGE, lambda: self.run(edge))
            self.raise_if_error(error_code)

    def on_map_current_event(self, msg: MapCurrentEvent, expected_map_id: int):
        error_code = (
            MapChangeError.UNEXPECTED_NEW_MAP if msg.map_id != expected_map_id else None
        )
        return self.finish(error_code)

    def use_map_change_transition(self, edge: Edge, transition: Transition):
        move_path = self.path_finding.find_path(
            self.game_state.get_map_movement_context(),
            self.game_state.map.map_point,
            {MapPoint.from_cell_id(transition.m_cellId)},
        )
        if move_path.end.cell_id != transition.m_cellId:
            self.logger.error(
                f"move path : {move_path} not ending at transition {transition}, invalid."
            )
            self.handle_invalid_transition(edge, transition)
            return self.run_timer(BASE_RANGE, lambda: self.run(edge))

        self.map_move_behavior.start(
            callback=partial(
                self.on_map_move_behavior_finished,
                transition_map_id=transition.m_transitionMapId,
                edge=edge,
                transition=transition,
            ),
            parent=self,
            move_path=move_path,
        )

    def on_map_move_behavior_finished(
        self,
        error_code: str | None,
        transition_map_id: int,
        edge: Edge,
        transition: Transition,
    ):
        if error_code is not None:
            if error_code in [
                MapMoveError.CANCELED_MOVEMENT,
                MapMoveError.INVALID_STARTING_POINT,
            ]:
                self.logger.warning("Canceled or invalid starting point, retry edge")
                return self.run_timer(BASE_RANGE, lambda: self.run(edge))
            elif error_code is MapMoveError.REFUSED:
                self.logger.error(
                    f"refused map move with mp {self.game_state.map.map_point}"
                )
                self.handle_invalid_transition(edge, transition)
                return self.run_timer(BASE_RANGE, lambda: self.run(edge))

            self.raise_if_error(error_code)

        self.map_change_behavior.start(
            callback=partial(
                self.on_map_change_behavior_finished, edge=edge, transition=transition
            ),
            parent=self,
            map_id=transition_map_id,
            expected_map_id=edge.m_to.m_mapId,
        )

    def on_map_change_behavior_finished(
        self, error_code: str | None, edge: Edge, transition: Transition
    ):
        if error_code is MapMoveError.INVALID_STARTING_POINT:
            return self.run_timer(BASE_RANGE, lambda: self.run(edge))
        elif error_code in [MapMoveError.REFUSED, MapChangeError.TIMEOUT]:
            self.logger.error("refused or timeout map change")
            self.handle_invalid_transition(edge, transition)
            return self.run_timer((1, 10), lambda: self.run(edge))
        self.finish(error_code)

    def handle_invalid_transition(self, edge: Edge, transition: Transition):
        self.logger.error(f"Forbidden edge : {edge} with transition : {transition}")
        self.game_state.map.forbidden_edge_transitions.add(
            (edge.m_from, edge.m_to, transition)
        )
