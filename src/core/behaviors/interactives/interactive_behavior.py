from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from datas.protos.non_obf.game.gamemap_pb2 import MapCurrentEvent
from datas.protos.non_obf.game.interactive_element_pb2 import (
    InteractiveUsedEvent,
    InteractiveUseErrorEvent,
    InteractiveUseRequest,
)
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.config import BASE_RANGE
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding

MAX_APPROACH_RETRIES: int = 3


class InteractiveError(StrEnum):
    USE_ERROR = auto()
    UNREACHABLE_ELEMENT = auto()
    SKILL_NOT_AVAILABLE = auto()


@dataclass
class InteractiveBehavior(Behavior):
    map_move_behavior: MapMoveBehavior
    path_finding: Pathfinding

    def run(
        self,
        element_mp: MapPoint,
        element_id: int,
        skill_id: int | None = None,
        ignore_server_range: bool = False,
        remaining_retries: int = MAX_APPROACH_RETRIES,
    ) -> None:
        """Walk to the client approach cell of `element_mp`, then use the element.

        `skill_id` defaults to the first enabled skill. Its instance uid is resolved right before
        sending, never captured here: the server disables the skills as soon as the element is
        used. `ignore_server_range`: see `Pathfinding.get_interactive_near_path`.
        """
        if self.game_state.map.is_in_map_transition:
            return self.finish()

        skill_ids = self.game_state.interactive.get_enabled_skill_ids(element_id)
        if len(skill_ids) == 0:
            self.logger.warning(f"Element {element_id} has no enabled skill left")
            return self.finish(InteractiveError.SKILL_NOT_AVAILABLE)

        move_path = self.path_finding.get_interactive_near_path(
            self.game_state.get_map_movement_context(),
            self.game_state.map.map_point,
            element_mp,
            skill_ids=skill_ids,
            ignore_server_range=ignore_server_range,
        )
        if move_path is None:
            self.logger.warning(f"No reachable approach cell for element {element_id} on {element_mp}")
            return self.finish(InteractiveError.UNREACHABLE_ELEMENT)

        if self.game_state.map.map_point.cell_id == move_path.end.cell_id:
            return self.use_interactive(element_id=element_id, skill_id=skill_id)

        self.event_manager.on(
            MapCurrentEvent,
            self.on_map_current_event,
            originator=self,
            once=True,
            override_on_self=True,
        )
        self.map_move_behavior.start(
            callback=partial(
                self.on_map_behavior_finish,
                element_mp=element_mp,
                element_id=element_id,
                skill_id=skill_id,
                ignore_server_range=ignore_server_range,
                remaining_retries=remaining_retries,
            ),
            parent=self,
            move_path=move_path,
        )

    def on_map_current_event(self, message: MapCurrentEvent) -> None:
        if self.game_state.fight.in_fight:
            self.logger.info("Interaction interrupted by fight context")
            self.stop()
            return
        self.finish(MapChangeError.UNEXPECTED_NEW_MAP)

    def on_map_behavior_finish(
        self,
        error_code: str | None,
        element_mp: MapPoint,
        element_id: int,
        skill_id: int | None,
        ignore_server_range: bool,
        remaining_retries: int,
    ):
        if error_code in [
            MapMoveError.INVALID_STARTING_POINT,
            MapMoveError.CANCELED_MOVEMENT,
        ]:
            if self.game_state.map.is_in_map_transition:
                self.logger.info("Is in map transition, finish")
                return self.finish()
            if remaining_retries <= 0:
                self.logger.warning(f"Giving up on element {element_id} after too many failed approaches")
                return self.finish(InteractiveError.UNREACHABLE_ELEMENT)

            self.logger.warning("Invalid starting point or canceled movement, recomputing approach cell")
            return self.run_timer(
                BASE_RANGE,
                lambda: self.run(
                    element_mp,
                    element_id,
                    skill_id,
                    ignore_server_range,
                    remaining_retries - 1,
                ),
            )
        elif error_code is not None:
            return self.finish(error_code)

        self.use_interactive(element_id, skill_id)

    def use_interactive(self, element_id: int, skill_id: int | None = None):
        skill = self.game_state.interactive.get_enabled_skill(element_id, skill_id)
        if skill is None:
            self.logger.warning(f"Skill {skill_id} is no longer enabled on element {element_id}, aborting")
            return self.finish(InteractiveError.SKILL_NOT_AVAILABLE)

        self.event_manager.on(
            InteractiveUsedEvent,
            partial(self.on_interactive_used_event, element_id=element_id),
            originator=self,
        )
        self.event_manager.on(
            InteractiveUseErrorEvent,
            self.on_interactive_use_error_event,
            originator=self,
            once=True,
            override_on_self=True,
        )
        request = InteractiveUseRequest(
            element_id=element_id, skill_instance_uid=skill.skill_instance_uid, specific_instance_id=0
        )
        self.event_manager.send(request)

    def on_interactive_used_event(self, msg: InteractiveUsedEvent, element_id: int):
        if msg.element_id == element_id:
            self.finish()

    def on_interactive_use_error_event(self, msg: InteractiveUseErrorEvent):
        return self.finish(InteractiveError.USE_ERROR)
