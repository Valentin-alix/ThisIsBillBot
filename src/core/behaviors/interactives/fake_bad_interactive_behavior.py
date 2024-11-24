from dataclasses import dataclass

from D3Mapping.d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveUseRequest,
)
from src.core.behaviors.behavior import Behavior


@dataclass
class FakeBadInteractiveBehavior(Behavior):
    def run(self):
        self.event_manager.send(
            InteractiveUseRequest(element_id=-1, skill_instance_uid=-1)
        )
        self.finish()
