import dataclasses
from threading import RLock

from D3Database.data_center.data_reader import DataReader
from D3Database.enums.category_item_enum import CategoryEnum
from D3Database.enums.type_item_enum import TypeItemEnum
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from src.core.config import DO_USE_GUILD_CHEST
from src.core.engine.items.item import GATHERER_ITEM_GIDS
from src.core.engine.monsters.drops import PROTECTOR_DROP_ITEM_IDS
from src.core.signals.player_signals import GameInfoSignals
from src.core.states.player_state import PlayerState
from src.core.states.state import State

# Global dict shared across all bots for guild chest items, keyed by server_id
# server_id -> tab -> gid -> ObjectItemInventory
CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER: dict[int, dict[int, dict[int, ObjectItemInventory]]] = {}
# Reserved quantities per server per tab per gid per bot_name to prevent race conditions
# server_id -> tab -> gid -> bot_name -> quantity
RESERVED_QUANTITIES_BY_SERVER: dict[int, dict[int, dict[int, dict[str, int]]]] = {}
CHEST_LOCK = RLock()

# Organisation par onglets
GIDS_BY_TAB = {
    1: GATHERER_ITEM_GIDS,
    2: DataReader().item_ids_by_type_id[TypeItemEnum.PLANCHE]
    | DataReader().item_ids_by_type_id[TypeItemEnum.PREPARATION]
    | DataReader().item_ids_by_type_id[TypeItemEnum.SUBSTRAT]
    | DataReader().item_ids_by_type_id[TypeItemEnum.ALLIAGE],
    3: {
        gid
        for gid in PROTECTOR_DROP_ITEM_IDS
        if DataReader().item_type_by_id[DataReader().item_by_id[gid].typeId].categoryId
        != CategoryEnum.CONSUMABLES
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

    def clear_state(self):
        self.tab_number = 1
        self.has_guild = False
        self.tabs = [1, 2, 3, 4]
        self.rank_id = 4

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
        return (
            self.player_state.is_sub
            and self.has_guild
            and DO_USE_GUILD_CHEST
            and self.rank_id <= 3
        )

    @staticmethod
    def set_tab_content(server_id: int, tab_number: int, objects: list[ObjectItemInventory]):
        with CHEST_LOCK:
            if server_id not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER:
                CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id] = {}
            CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id][tab_number] = {
                obj.item.gid: obj for obj in objects
            }

    @staticmethod
    def get_item_by_uid(server_id: int, tab_number: int, object_uid: int) -> ObjectItemInventory | None:
        with CHEST_LOCK:
            if server_id not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER:
                return None
            if tab_number not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id]:
                return None
            return next(
                (
                    item
                    for item in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id][tab_number].values()
                    if item.item.uid == object_uid
                ),
                None,
            )

    @staticmethod
    def update_item_quantity(server_id: int, tab_number: int, object_uid: int, quantity_delta: int):
        with CHEST_LOCK:
            if server_id not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER:
                return
            if tab_number not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id]:
                return

            item = next(
                (
                    item
                    for item in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id][tab_number].values()
                    if item.item.uid == object_uid
                ),
                None,
            )

            if item is None:
                return

            new_quantity = item.item.quantity + quantity_delta
            item.item.quantity = new_quantity

            if new_quantity == 0:
                CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id][tab_number].pop(item.item.gid)

    @staticmethod
    def get_item_by_gid(server_id: int, tab_number: int, gid: int) -> ObjectItemInventory | None:
        with CHEST_LOCK:
            if server_id not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER:
                return None
            if tab_number not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id]:
                return None
            return CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id][tab_number].get(gid)

    @staticmethod
    def get_all_items_by_gid(server_id: int) -> dict[int, ObjectItemInventory]:
        with CHEST_LOCK:
            if server_id not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER:
                return {}
            return {
                gid: obj
                for object_by_gid in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id].values()
                for gid, obj in object_by_gid.items()
            }

    @staticmethod
    def get_storage_objects_by_gid(server_id: int) -> dict[int, ObjectItemInventory]:
        with CHEST_LOCK:
            all_items = GuildChestState.get_all_items_by_gid(server_id)
            available_items: dict[int, ObjectItemInventory] = {}
            for gid, item in all_items.items():
                tab = GuildChestState.get_tab_for_gid(server_id, gid)
                if tab is None:
                    continue
                available_quantity = GuildChestState.get_available_quantity(server_id, tab, gid)
                if available_quantity > 0:
                    item_copy = type(item)()
                    item_copy.CopyFrom(item)
                    item_copy.item.quantity = available_quantity
                    available_items[gid] = item_copy
            return available_items

    @staticmethod
    def tab_exists(server_id: int, tab_number: int) -> bool:
        with CHEST_LOCK:
            if server_id not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER:
                return False
            return tab_number in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id]

    @staticmethod
    def get_tab_size(server_id: int, tab_number: int) -> int:
        with CHEST_LOCK:
            if server_id not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER:
                return 0
            if tab_number not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id]:
                return 0
            return len(CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id][tab_number])

    @staticmethod
    def get_tab_for_gid(server_id: int, gid: int) -> int | None:
        with CHEST_LOCK:
            if server_id not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER:
                return None
            for tab, items in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[server_id].items():
                if gid in items:
                    return tab
            return None

    @staticmethod
    def get_available_quantity(server_id: int, tab_number: int, gid: int) -> int:
        with CHEST_LOCK:
            item = GuildChestState.get_item_by_gid(server_id, tab_number, gid)
            if item is None:
                return 0

            total_quantity = item.item.quantity
            if server_id not in RESERVED_QUANTITIES_BY_SERVER:
                return total_quantity

            if tab_number not in RESERVED_QUANTITIES_BY_SERVER[server_id]:
                return total_quantity

            if gid not in RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number]:
                return total_quantity

            reserved = sum(RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number][gid].values())
            return max(0, total_quantity - reserved)

    @staticmethod
    def reserve_quantity(server_id: int, tab_number: int, gid: int, quantity: int, bot_name: str):
        with CHEST_LOCK:
            if server_id not in RESERVED_QUANTITIES_BY_SERVER:
                RESERVED_QUANTITIES_BY_SERVER[server_id] = {}
            if tab_number not in RESERVED_QUANTITIES_BY_SERVER[server_id]:
                RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number] = {}
            if gid not in RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number]:
                RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number][gid] = {}

            current_reserved = RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number][gid].get(bot_name, 0)
            RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number][gid][bot_name] = current_reserved + quantity

    @staticmethod
    def release_reservation(server_id: int, tab_number: int, gid: int, quantity: int, bot_name: str):
        with CHEST_LOCK:
            if server_id not in RESERVED_QUANTITIES_BY_SERVER:
                return
            if tab_number not in RESERVED_QUANTITIES_BY_SERVER[server_id]:
                return
            if gid not in RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number]:
                return
            if bot_name not in RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number][gid]:
                return

            current = RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number][gid][bot_name]
            new_quantity = max(0, current - quantity)

            if new_quantity == 0:
                RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number][gid].pop(bot_name)
                if len(RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number][gid]) == 0:
                    RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number].pop(gid)
                if len(RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number]) == 0:
                    RESERVED_QUANTITIES_BY_SERVER[server_id].pop(tab_number)
            else:
                RESERVED_QUANTITIES_BY_SERVER[server_id][tab_number][gid][bot_name] = new_quantity

    @staticmethod
    def clear_all_reservations_for_bot(server_id: int, bot_name: str):
        with CHEST_LOCK:
            if server_id not in RESERVED_QUANTITIES_BY_SERVER:
                return
            for tab_reservations in RESERVED_QUANTITIES_BY_SERVER[server_id].values():
                for gid_reservations in tab_reservations.values():
                    gid_reservations.pop(bot_name, None)
