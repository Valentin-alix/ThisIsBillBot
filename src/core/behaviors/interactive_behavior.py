from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.interactive_element_pb2 import (
    InteractiveUseRequest,
    InteractiveUsedEvent,
)
from src.core.behaviors.behavior import Behavior, EndCode
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.states.player_state import PlayerState


@dataclass
class InteractiveBehavior(Behavior):
    map_behavior: MapMoveBehavior
    player_state: PlayerState

    def run(
        self,
        move_path: MovementPath,
        element_id: int,
        skill_instance_uid: int,
    ):
        self.event_manager.on(
            InteractiveUsedEvent,
            partial(self.on_interactive_used_event, element_id=element_id),
            originator=self,
        )
        if self.player_state.map_point.cell_id == move_path.end.cell_id:
            self._use_interactive(
                element_id=element_id, skill_instance_uid=skill_instance_uid
            )
        else:
            self.map_behavior.start(
                callback=partial(
                    self.on_map_moved,
                    element_id=element_id,
                    skill_instance_uid=skill_instance_uid,
                ),
                parent=self,
                move_path=move_path,
            )

    def on_map_moved(self, code: EndCode, element_id: int, skill_instance_uid: int):
        if code == code.SUCCESS:
            self._use_interactive(element_id, skill_instance_uid)

    def _use_interactive(self, element_id: int, skill_instance_uid: int):
        request = InteractiveUseRequest(
            element_id=element_id,
            skill_instance_uid=skill_instance_uid,
            specific_instance_id=0,
        )
        self.event_manager.send(request)

    def on_interactive_used_event(self, msg: InteractiveUsedEvent, element_id: int):
        if msg.element_id == element_id:
            self.finish()
