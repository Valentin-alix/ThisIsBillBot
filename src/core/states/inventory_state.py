import dataclasses
from dataclasses import dataclass

from src.core.states.state import State
from db_dofus_unity.protos.game.common_pb2 import ObjectItemInventory


@dataclass
class InventoryState(State):
    inventory_weight: int = dataclasses.field(init=False, default=0)
    weight_max: int = dataclasses.field(init=False, default=1)
    objects: list[ObjectItemInventory] = dataclasses.field(
        init=False, default_factory=lambda: []
    )
    kamas: int = dataclasses.field(init=False, default=0)
