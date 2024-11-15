from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveUsedEvent,
    InteractiveUseErrorEvent,
    InteractiveUseRequest,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.config.timings import BASE_RANGE
from src.core.logic.map.path_finding.movement_path import MovementPath
from src.core.logic.map.path_finding.path_finding import Pathfinding


class InteractiveError(StrEnum):
    USE_ERROR = auto()


@dataclass
class InteractiveBehavior(Behavior):
    map_move_behavior: MapMoveBehavior
    path_finding: Pathfinding

    def run(
        self,
        move_path: MovementPath | None,
        element_id: int,
        skill_instance_uid: int,
    ):
        if self.game_state.map._is_in_map_transition:
            return
        if (
            move_path is None
            or self.game_state.player.map_point.cell_id == move_path.end.cell_id
        ):
            return self.use_interactive(
                element_id=element_id, skill_instance_uid=skill_instance_uid
            )

        self.map_move_behavior.start(
            callback=partial(
                self.on_map_behavior_finish,
                element_id=element_id,
                skill_instance_uid=skill_instance_uid,
                old_move_path=move_path,
            ),
            parent=self,
            move_path=move_path,
        )

    def on_map_behavior_finish(
        self,
        error_code: str | None,
        element_id: int,
        skill_instance_uid: int,
        old_move_path: MovementPath,
    ):
        if error_code in [
            MapMoveError.INVALID_STARTING_POINT,
            MapMoveError.CANCELED_MOVEMENT,
        ]:
            if self.game_state.map._is_in_map_transition:
                return self.finish()

            move_path = self.path_finding.find_path(
                self.game_state.player.map_point, {old_move_path.end}
            )
            self.logger.warning(
                "Invalid starting point or canceled movement, let's retry interactive"
            )
            return self.run_timer(
                BASE_RANGE, lambda: self.run(move_path, element_id, skill_instance_uid)
            )
        elif error_code is not None:
            return self.finish(error_code)

        self.use_interactive(element_id, skill_instance_uid)

    def use_interactive(self, element_id: int, skill_instance_uid: int):
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
        )
        request = InteractiveUseRequest(
            element_id=element_id,
            skill_instance_uid=skill_instance_uid,
            specific_instance_id=0,
        )
        self.event_manager.send(request)

    def on_interactive_used_event(self, msg: InteractiveUsedEvent, element_id: int):
        if msg.element_id == element_id:
            self.finish()

    def on_interactive_use_error_event(self, msg: InteractiveUseErrorEvent):
        return self.finish(InteractiveError.USE_ERROR)
