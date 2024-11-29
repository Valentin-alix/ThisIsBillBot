from datas.protos.non_obf.game.common_pb2 import (
    ObjectItem,
    ObjectItemInventory,
)
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeObjectMoveRequest,
    ExchangeStartedWithMultiTabStorageEvent,
)
from datas.protos.non_obf.game.guild_member_pb2 import (
    GuildMembershipEvent,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    StorageInventoryContentEvent,
)
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER
from tests.test_states.state_test_base import StateTestBase

TEST_SERVER_ID = 1


class TestGuildChestState(StateTestBase):
    def setUp(self):
        super().setUp()
        CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER.clear()
        self.game_state.player._server_id = TEST_SERVER_ID

    def test_initial_state(self):
        assert self.game_state.guild_chest.tab_number == 1
        assert self.game_state.guild_chest.has_guild is False
        assert self.game_state.guild_chest.tabs == [1, 2, 3, 4]

    def test_clear_state_resets_values(self):
        self.game_state.guild_chest.tab_number = 3
        self.game_state.guild_chest.has_guild = True
        self.game_state.guild_chest.tabs = [1, 2]

        self.game_state.guild_chest.clear_state()

        assert self.game_state.guild_chest.tab_number == 1
        assert self.game_state.guild_chest.has_guild is False
        assert self.game_state.guild_chest.tabs == [1, 2, 3, 4]

    def test_guild_membership_event_sets_has_guild(self):
        assert self.game_state.guild_chest.has_guild is False

        self.inject(GuildMembershipEvent())

        assert self.game_state.guild_chest.has_guild is True

    def test_exchange_started_with_multi_tab_storage_sets_tab_number(self):
        msg = ExchangeStartedWithMultiTabStorageEvent(
            tab_number=2, storage_max_slot=100
        )

        self.inject(msg)

        assert self.game_state.guild_chest.tab_number == 2

    def test_exchange_started_with_tab_number_100_uses_storage_max_slot(self):
        msg = ExchangeStartedWithMultiTabStorageEvent(
            tab_number=100, storage_max_slot=5
        )

        self.inject(msg)

        assert self.game_state.guild_chest.tab_number == 5

    def test_storage_inventory_content_populates_chest(self):
        msg_start = ExchangeStartedWithMultiTabStorageEvent(
            tab_number=1, storage_max_slot=100
        )
        self.inject(msg_start)

        objects = [
            ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10)),
            ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=5)),
        ]
        msg_content = StorageInventoryContentEvent(objects=objects)

        self.inject(msg_content)

        assert 1 in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID]
        assert 100 in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][1]
        assert 200 in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][1]
        assert CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][1][100].item.quantity == 10

    def test_exchange_object_move_from_inventory_to_chest(self):
        self.game_state.guild_chest.tab_number = 1
        CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID] = {}
        CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][1] = {
            100: ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=5))
        }
        inventory_item = ObjectItemInventory(
            item=ObjectItem(uid=10, gid=100, quantity=20)
        )
        self.game_state.inventory.add_object(inventory_item)

        msg_start = ExchangeStartedWithMultiTabStorageEvent(
            tab_number=1, storage_max_slot=100
        )
        self.inject(msg_start)

        msg_move = ExchangeObjectMoveRequest(object_uid=1, quantity=3)
        self.inject(msg_move)

        assert CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][1][100].item.quantity == 8

    def test_exchange_object_move_removes_item_when_quantity_zero(self):
        self.game_state.guild_chest.tab_number = 1
        CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID] = {}
        CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][1] = {
            100: ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=5))
        }

        msg_start = ExchangeStartedWithMultiTabStorageEvent(
            tab_number=1, storage_max_slot=100
        )
        self.inject(msg_start)

        msg_move = ExchangeObjectMoveRequest(object_uid=1, quantity=-5)
        self.inject(msg_move)

        assert 100 not in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][1]

    def test_can_access_guild_chest_requires_sub_and_guild(self):
        self.game_state.guild_chest.has_guild = False

        assert self.game_state.guild_chest.can_access_guild_chest is False

        self.game_state.guild_chest.has_guild = True
        assert self.game_state.guild_chest.can_access_guild_chest is False

    def test_multiple_tabs_storage(self):
        msg_start_tab1 = ExchangeStartedWithMultiTabStorageEvent(
            tab_number=1, storage_max_slot=100
        )
        self.inject(msg_start_tab1)

        objects_tab1 = [
            ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10)),
        ]
        self.inject(StorageInventoryContentEvent(objects=objects_tab1))

        assert 100 in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][1]

        msg_start_tab2 = ExchangeStartedWithMultiTabStorageEvent(
            tab_number=2, storage_max_slot=100
        )
        self.inject(msg_start_tab2)

        objects_tab2 = [
            ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=20)),
        ]
        self.inject(StorageInventoryContentEvent(objects=objects_tab2))

        assert 100 in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][1]
        assert 200 in CHEST_OBJECT_BY_GID_BY_TAB_BY_SERVER[TEST_SERVER_ID][2]
