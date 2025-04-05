import dataclasses

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.item import (
    CategoryItemEnum,
    ItemTypeEnum,
)

from src import const
from src.core.config import DO_USE_GUILD_CHEST
from src.core.engine.items.item import GATHERER_ITEM_GIDS, PROTECTOR_DROP_ITEM_IDS
from src.core.signals.player_signals import GameInfoSignals
from src.core.states.guild_chest_storage import GuildChestStorage
from src.core.states.player_state import PlayerState
from src.core.states.state import State

GIDS_BY_TAB = {
    1: GATHERER_ITEM_GIDS,
    2: DataReader().item_ids_by_type_id[ItemTypeEnum.PLANCHE]
    | DataReader().item_ids_by_type_id[ItemTypeEnum.PREPARATION]
    | DataReader().item_ids_by_type_id[ItemTypeEnum.SUBSTRAT]
    | DataReader().item_ids_by_type_id[ItemTypeEnum.ALLIAGE],
    3: {
        gid
        for gid in PROTECTOR_DROP_ITEM_IDS
        if DataReader().item_type_by_id[DataReader().item_by_id[gid].typeId].categoryId
        != CategoryItemEnum.CONSUMABLES
    },
}
TAB_BY_GID = {gid: tab for tab, gids in GIDS_BY_TAB.items() for gid in gids}


@dataclasses.dataclass
class GuildChestState(State):
    player_state: PlayerState
    game_info_signals: GameInfoSignals
    _tab_number: int = dataclasses.field(init=False, default=1)
    _has_guild: bool = dataclasses.field(init=False, default=False)
    tabs: list[int] = dataclasses.field(
        init=False, default_factory=lambda: [1, 2, 3, 4]
    )
    rank_id: int = dataclasses.field(init=False, default=4)

    def clear_state(self) -> None:
        self.tab_number = 1
        self.has_guild = False
        self.tabs = [1, 2, 3, 4]
        self.rank_id = 4

    @property
    def storage(self) -> GuildChestStorage:
        return GuildChestStorage.for_server(self.player_state.server_id)

    @property
    def tab_number(self) -> int:
        return self._tab_number

    @tab_number.setter
    def tab_number(self, value: int) -> None:
        self._tab_number = value
        if const.DEBUG:
            self.game_info_signals.tab_number.emit(value)

    @property
    def has_guild(self) -> bool:
        return self._has_guild

    @has_guild.setter
    def has_guild(self, value: bool) -> None:
        self._has_guild = value
        if const.DEBUG:
            self.game_info_signals.has_guild.emit(value)

    @property
    def can_access_guild_chest(self) -> bool:
        return (
            self.player_state.is_sub
            and self.has_guild
            and DO_USE_GUILD_CHEST
            and self.rank_id <= 3
        )
