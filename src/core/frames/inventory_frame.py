from dataclasses import dataclass

from db_dofus_unity.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
    InventoryContentEvent,
)
from src.core.frames.frame import Frame
from src.core.states.inventory_state import InventoryState


@dataclass
class InventoryFrame(Frame):
    inventory_state: InventoryState

    def __post_init__(self):
        self.event_manager.on(
            InventoryWeightEvent,
            self.on_inventory_weight_event,
            originator=self,
        )
        self.event_manager.on(
            InventoryContentEvent, self.on_inventory_content_event, originator=self
        )

    def on_inventory_weight_event(self, message: InventoryWeightEvent):
        self.inventory_state.inventory_weight = message.inventory_weight
        self.inventory_state.weight_max = message.weight_max

    def on_inventory_content_event(self, msg: InventoryContentEvent):
        self.inventory_state.objects = msg.objects
