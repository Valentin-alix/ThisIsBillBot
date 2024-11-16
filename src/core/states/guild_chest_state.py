import dataclasses

from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from src.core.config import DO_USE_GUILD_CHEST
from src.core.signals.player_signals import GameInfoSignals
from src.core.states.player_state import PlayerState
from src.core.states.state import State

# Global dict shared across all bots for guild chest items
CHEST_OBJECT_BY_GID_BY_TAB: dict[int, dict[int, ObjectItemInventory]] = {}


@dataclasses.dataclass
class GuildChestState(State):
    player_state: PlayerState
    game_info_signals: GameInfoSignals
    _tab_number: int = dataclasses.field(init=False, default=1)
    _has_guild: bool = dataclasses.field(init=False, default=False)
    tabs: list[int] = dataclasses.field(
        init=False, default_factory=lambda: [1, 2, 3, 4]
    )

    def clear_state(self):
        self.tab_number = 1
        self.tabs = [1, 2, 3, 4]
        self.has_guild = False

    @property
    def tab_number(self) -> int:
        return self._tab_number

    @tab_number.setter
    def tab_number(self, value: int):
        self._tab_number = value
        self.game_info_signals.tab_number.emit(value)

    @property
    def has_guild(self) -> bool:
        return self._has_guild

    @has_guild.setter
    def has_guild(self, value: bool):
        self._has_guild = value
        self.game_info_signals.has_guild.emit(value)

    @property
    def can_access_guild_chest(self):
        return self.player_state.is_sub and self.has_guild and DO_USE_GUILD_CHEST
