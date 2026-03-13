from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import MapCurrentEvent
from DBDofusUnity.datas.protos.non_obf.game.interactive_element_pb2 import (
    InteractiveUsedEvent,
    InteractiveUseErrorEvent,
    InteractiveUseRequest,
)
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.behaviors.movements.map_movement_cancel_behavior import MapMovementCancelBehavior
from src.core.config import STATIC_INTERACTION_CANCEL_PROBABILITY
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.services.human_timings import HumanTimingsService

MAX_APPROACH_RETRIES: int = 3


class InteractiveError(StrEnum):
    USE_ERROR = auto()
    UNREACHABLE_ELEMENT = auto()
    SKILL_NOT_AVAILABLE = auto()


@dataclass
class InteractiveBehavior(Behavior):
    map_move_behavior: MapMoveBehavior
    map_movement_cancel_behavior: MapMovementCancelBehavior
    path_finding: Pathfinding

    def run(
        self,
        element_mp: MapPoint,
        element_id: int,
        skill_id: int | None = None,
        ignore_server_range: bool = False,
        remaining_retries: int = MAX_APPROACH_RETRIES,
        movement_cancel_probability: float = STATIC_INTERACTION_CANCEL_PROBABILITY,
        pre_interaction_delay: float = 0,
    ) -> None:
        """Resolve the skill instance just before sending: using an element disables its current skills."""
        assert 0 <= movement_cancel_probability <= 1, (
            "Interaction cancellation probability must be between zero and one"
        )
        assert pre_interaction_delay >= 0, "Interaction delay must be positive"
        if self.game_state.map.is_in_map_transition:
            return self.finish()

        self.ensure_dialog_closed(
            partial(
                self.approach_and_use,
                element_mp,
                element_id,
                skill_id,
                ignore_server_range,
                remaining_retries,
                movement_cancel_probability,
                pre_interaction_delay,
            )
        )

    def approach_and_use(
        self,
        element_mp: MapPoint,
        element_id: int,
        skill_id: int | None,
        ignore_server_range: bool,
        remaining_retries: int,
        movement_cancel_probability: float,
        pre_interaction_delay: float,
    ) -> None:
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

        self.event_manager.on(
            MapCurrentEvent,
            self.on_map_current_event,
            originator=self,
            once=True,
            override_on_self=True,
        )

        if self.game_state.map.map_point.cell_id == move_path.end.cell_id:
            return self._use_interactive_after_delay(
                element_id,
                skill_id,
                pre_interaction_delay,
            )

        callback = partial(
            self.on_map_behavior_finish,
            element_mp=element_mp,
            element_id=element_id,
            skill_id=skill_id,
            ignore_server_range=ignore_server_range,
            remaining_retries=remaining_retries,
            movement_cancel_probability=movement_cancel_probability,
            pre_interaction_delay=pre_interaction_delay,
        )
        if movement_cancel_probability == 0:
            self.map_move_behavior.start(
                callback=callback,
                parent=self,
                move_path=move_path,
            )
            return
        self.map_movement_cancel_behavior.start(
            callback=callback,
            parent=self,
            final_move_path=move_path,
            cancellation_probability=movement_cancel_probability,
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
        movement_cancel_probability: float,
        pre_interaction_delay: float,
    ) -> None:
        if error_code is MapMoveError.UNEXPECTED_NEW_MAP:
            self.finish(MapChangeError.UNEXPECTED_NEW_MAP)
            return
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
                HumanTimingsService().get_timing_base_action(),
                lambda: self.run(
                    element_mp,
                    element_id,
                    skill_id,
                    ignore_server_range,
                    remaining_retries - 1,
                    movement_cancel_probability,
                    pre_interaction_delay,
                ),
            )
        elif error_code is not None:
            return self.finish(error_code)

        self._use_interactive_after_delay(element_id, skill_id, pre_interaction_delay)

    def _use_interactive_after_delay(
        self,
        element_id: int,
        skill_id: int | None,
        pre_interaction_delay: float,
    ) -> None:
        if pre_interaction_delay == 0:
            self.use_interactive(element_id, skill_id)
            return
        self.run_timer(
            pre_interaction_delay,
            lambda: self.use_interactive(element_id, skill_id),
        )

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
