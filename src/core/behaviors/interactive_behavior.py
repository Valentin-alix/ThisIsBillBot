from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from protos.game.interactive_element_pb2 import (
    InteractiveUseRequest,
    InteractiveUsedEvent,
    InteractiveUseErrorEvent,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.logic.grid.path_finding.movement_path import MovementPath


class InteractiveError(StrEnum):
    USE_ERROR = auto()


@dataclass
class InteractiveBehavior(Behavior):
    map_move_behavior: MapMoveBehavior

    def run(
        self,
        move_path: MovementPath | None,
        element_id: int,
        skill_instance_uid: int,
    ):
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
            ),
            parent=self,
            move_path=move_path,
        )

    def on_map_behavior_finish(
        self, error_code: str | None, element_id: int, skill_instance_uid: int
    ):
        if error_code is not None:
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
