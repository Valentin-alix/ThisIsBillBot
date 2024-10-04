from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.inventory_pb2 import (
    InventoryWeightEvent,
    InventoryContentEvent,
)
from src.core.handlers.handler import Handler
from src.core.states.inventory_state import InventoryState


@dataclass
class InventoryHandler(Handler):
    inventory_state: InventoryState

    def __post_init__(self):
        self.msg_event.received_game_msg.connect(
            self.on_inventory_weight_event, InventoryWeightEvent
        )
        self.msg_event.received_game_msg.connect(
            self.on_inventory_content_event, InventoryContentEvent
        )

    def on_inventory_weight_event(self, _, message: InventoryWeightEvent):
        self.inventory_state.inventory_weight = message

    def on_inventory_content_event(self, _, message: InventoryContentEvent):
        self.inventory_state.inventory_content = message
