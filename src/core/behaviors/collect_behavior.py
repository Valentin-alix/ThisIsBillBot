from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.interactive_element_pb2 import (
    InteractiveElementUpdatedEvent,
)
from src.common.logger import Logger
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.player_state import PlayerState
from src.interfaces.models.collectable import Collectable


@dataclass
class CollectBehavior(Behavior):
    path_finding: Pathfinding
    interactive_behavior: InteractiveBehavior
    interactive_state: InteractiveState
    player_state: PlayerState
    inventory_state: InventoryState

    def run(self, move_path: MovementPath, collectable: Collectable) -> bool:
        Logger().info(f"Collecting at {move_path.end.point}")
        self.event_manager.on(
            InteractiveElementUpdatedEvent,
            partial(
                self.interactive_updated,
                element_id=collectable.interactive_element.interactive_element.element_id,
            ),
            originator=self,
        )
        self.interactive_behavior.start(
            callback=None,
            parent=self,
            move_path=move_path,
            element_id=collectable.interactive_element.interactive_element.element_id,
            skill_instance_uid=collectable.skill.skill_instance_uid,
        )
        return True

    def interactive_updated(
        self, message: InteractiveElementUpdatedEvent, element_id: int
    ):
        if (
            message.interactive_element.element_id == element_id
            and self.interactive_state.interactive_elements_by_id[element_id].state == 1
        ):
            self.finish()
