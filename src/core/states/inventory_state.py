import dataclasses
from dataclasses import dataclass

from db_dofus_unity.protos.game.common_pb2 import ObjectItemInventory
from src.core.states.state import State


@dataclass
class InventoryState(State):
    inventory_weight: int = dataclasses.field(init=False, default=0)
    weight_max: int = dataclasses.field(init=False, default=1)
    objects: list[ObjectItemInventory] = dataclasses.field(
        init=False, default_factory=list
    )

    @property
    def is_full_pods(self) -> bool:
        return self.inventory_weight / self.weight_max >= 0.95
