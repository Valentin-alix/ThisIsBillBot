from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.haven_bag_pb2 import (
    HavenBagEnterRequest,
    HavenBagPermissionsUpdateEvent,
)
from db_dofus_unity.protos.game.teleportation_pb2 import TeleportRequest, Teleporter
from src.consts import BASE_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.states.interactive_state import InteractiveState
from src.core.states.player_state import PlayerState


@dataclass
class WaypointBehavior(Behavior):
    player_state: PlayerState
    interactive_state: InteractiveState
    interactive_behavior: InteractiveBehavior

    def run(self, map_id: int) -> None:
        self.event_manager.on(
            HavenBagPermissionsUpdateEvent,
            callback=partial(self.on_entered_havre_sac, map_id=map_id),
            originator=self,
            once=True,
        )

        req = HavenBagEnterRequest(owner=self.player_state.character_id)
        self.event_manager.send(req)

    def on_entered_havre_sac(self, msg: HavenBagPermissionsUpdateEvent, map_id: int):
        zaap = self.interactive_state.interactive_element_by_id[537242]
        self.run_timer(
            BASE_RANGE,
            lambda: self.interactive_behavior.start(
                parent=self,
                callback=partial(self.on_zaap_used, map_id=map_id),
                move_path=MovementPath(
                    start=self.player_state.map_point,
                    end=self.player_state.map_point,
                    path=[],
                ),
                element_id=zaap.element_id,
                skill_instance_uid=zaap.enabled_skills[0].skill_instance_uid,
            ),
        )

    def on_zaap_used(self, error_code: str | None, map_id: int):
        if error_code is not None:
            return
        req = TeleportRequest(
            source_type=Teleporter.TELEPORTER_HAVEN_BAG, map_id=map_id
        )
        self.run_timer(BASE_RANGE, lambda: self.event_manager.send(req))
