from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.interactive_element_pb2 import (
    StatedElementUpdatedEvent,
)
from src.common.logger import Logger
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.interfaces.models.collectable import Collectable


@dataclass
class CollectBehavior(Behavior):
    interactive_behavior: InteractiveBehavior

    def run(self, move_path: MovementPath, collectable: Collectable) -> bool:
        Logger().info(f"Collecting at {move_path.end}")
        self.event_manager.on(
            StatedElementUpdatedEvent,
            partial(
                self.interactive_updated,
                element_id=collectable.interactive_element.element_id,
            ),
            originator=self,
        )
        self.interactive_behavior.start(
            callback=None,
            parent=self,
            move_path=move_path,
            element_id=collectable.interactive_element.element_id,
            skill_instance_uid=collectable.skill.skill_instance_uid,
        )
        return True

    def interactive_updated(self, msg: StatedElementUpdatedEvent, element_id: int):
        if (
            msg.stated_element.element_id == element_id
            and msg.stated_element.state == 1
        ):
            self.finish()
