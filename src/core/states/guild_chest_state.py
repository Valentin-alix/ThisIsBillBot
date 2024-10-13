import dataclasses

from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from src.core.states.state import State

CHEST_OBJECT_BY_GID_BY_TAB: dict[int, dict[int, ObjectItemInventory]] = {}


@dataclasses.dataclass
class GuildChestState(State):
    tab_number: int = dataclasses.field(init=False, default=1)

    def clear_state(self):
        self.tab_number = 1
