import dataclasses

from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory

from src.core.states.state import State
from src.signals.player_signals import GameInfoSignals

CHEST_OBJECT_BY_GID_BY_TAB: dict[int, dict[int, ObjectItemInventory]] = {}


@dataclasses.dataclass
class GuildChestState(State):
    game_info_signals: GameInfoSignals
    _tab_number: int = dataclasses.field(init=False, default=1)
    tabs: list[int] = dataclasses.field(
        init=False, default_factory=lambda: [1, 2, 3, 4]
    )

    def clear_state(self):
        self.tab_number = 1
        self.tabs = [1, 2, 3, 4]

    @property
    def tab_number(self) -> int:
        return self._tab_number

    @tab_number.setter
    def tab_number(self, value: int):
        self._tab_number = value
        self.game_info_signals.tab_number.emit(value)
