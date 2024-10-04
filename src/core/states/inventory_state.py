import dataclasses
from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.inventory_pb2 import (
    InventoryWeightEvent,
    InventoryContentEvent,
)
from src.core.states.state import State


@dataclass
class InventoryState(State):
    inventory_weight: InventoryWeightEvent = dataclasses.field(
        init=False, default_factory=InventoryWeightEvent
    )
    inventory_content: InventoryContentEvent = dataclasses.field(
        init=False, default_factory=InventoryContentEvent
    )
