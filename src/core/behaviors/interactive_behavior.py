from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.gamemap_pb2 import MapMovementConfirmRequest
from com.ankama.dofus.server.game.protocol.interactive.element_pb2 import (
    InteractiveUseRequest,
)
from src.core.behaviors.map_behavior import MapBehavior
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.states.player_state import PlayerState
from src.signals.message_events import MessageEvents


@dataclass
class InteractiveBehavior:
    map_behavior: MapBehavior
    player_state: PlayerState
    msg_event: MessageEvents

    def move_and_use_interactive(
        self, move_path: MovementPath, element_id: int, skill_instance_uid: int
    ):
        def on_moved(_, message: MapMovementConfirmRequest):
            self.msg_event.received_game_msg.disconnect(
                on_moved, MapMovementConfirmRequest
            )
            self._use_interactive(
                element_id=element_id, skill_instance_uid=skill_instance_uid
            )

        if self.player_state.map_point.map_point == move_path.end.cell_id:
            self._use_interactive(
                element_id=element_id, skill_instance_uid=skill_instance_uid
            )
        else:
            self.msg_event.received_game_msg.connect(
                on_moved, MapMovementConfirmRequest, weak=False
            )
            self.map_behavior.send_move_path(move_path)

    def _use_interactive(self, element_id: int, skill_instance_uid: int):
        request = InteractiveUseRequest(
            element_id=element_id,
            skill_instance_uid=skill_instance_uid,
            specific_instance_id=0,
        )
        self.msg_event.send_game_msg.send(request)
