from copy import deepcopy

from datas.protos.non_obf.game.common_pb2 import (
    ObjectItem,
    ObjectItemInventory,
)
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeStartedWithMultiTabStorageEvent,
)
from datas.protos.non_obf.game.guild_member_pb2 import (
    GuildMembershipEvent,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    MultiTabStorageEvent,
    StorageTab,
    StorageInventoryContentEvent,
    StorageObjectRemovedEvent,
    StorageObjectsRemovedEvent,
    StorageObjectsUpdateEvent,
    StorageObjectUpdateEvent,
)

from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.states.guild_chest_storage import GuildChestStorage, _STORAGE_REGISTRY
from tests.test_states.state_test_base import TEST_ACCOUNT, StateTestBase

TEST_SERVER_ID = 1


class TestGuildChestState(StateTestBase):
    def setUp(self):
        super().setUp()
        _STORAGE_REGISTRY.clear()
        self.game_state.player._server_id = TEST_SERVER_ID

    def storage(self, server_id: int = TEST_SERVER_ID) -> GuildChestStorage:
        return GuildChestStorage.for_server(server_id)

    def create_other_bot(self, login: str, server_id: int):
        other_account = deepcopy(TEST_ACCOUNT)
        other_account["apikey"]["login"] = login
        other_account["apikey"]["certificate"]["login"] = login
        other_bot = BotFactory.create_bot(
            SharedSignals(), account=other_account, is_fake=True
        )
        self.addCleanup(other_bot._logger.close)
        other_bot.game_state.player._server_id = server_id
        return other_bot

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

    def test_multi_tab_storage_event_sets_available_tabs(self):
        self.inject(
            MultiTabStorageEvent(
                tabs=[
                    StorageTab(tab_number=2),
                    StorageTab(tab_number=4),
                ]
            )
        )

        assert self.game_state.guild_chest.tabs == [2, 4]

    def test_storage_inventory_content_populates_chest(self):
        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))

        objects = [
            ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10)),
            ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=5)),
        ]
        self.inject(StorageInventoryContentEvent(objects=objects))

        assert self.storage().get_item_by_gid(1, 100) is not None
        assert self.storage().get_item_by_gid(1, 200) is not None
        assert self.storage().get_item_by_gid(1, 100).item.quantity == 10  # type: ignore[union-attr]

    def test_storage_object_update_event_updates_existing_item(self):
        self.game_state.guild_chest.tab_number = 1
        self.storage().set_tab_content(
            1, [ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=5))]
        )

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(
            StorageObjectUpdateEvent(
                object=ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=8))
            )
        )

        item = self.storage().get_item_by_gid(1, 100)
        assert item is not None
        assert item.item.quantity == 8

    def test_storage_object_update_event_adds_new_item(self):
        self.game_state.guild_chest.tab_number = 1
        self.storage().set_tab_content(1, [])

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(
            StorageObjectUpdateEvent(
                object=ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=7))
            )
        )

        item = self.storage().get_item_by_gid(1, 200)
        assert item is not None
        assert item.item.quantity == 7

    def test_storage_objects_update_event_updates_multiple_items(self):
        self.game_state.guild_chest.tab_number = 1
        self.storage().set_tab_content(
            1, [ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=5))]
        )

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(
            StorageObjectsUpdateEvent(
                objects=[
                    ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=9)),
                    ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=4)),
                ]
            )
        )

        assert self.storage().get_item_by_gid(1, 100).item.quantity == 9  # type: ignore[union-attr]
        assert self.storage().get_item_by_gid(1, 200).item.quantity == 4  # type: ignore[union-attr]

    def test_storage_object_removed_event_removes_item(self):
        self.game_state.guild_chest.tab_number = 1
        self.storage().set_tab_content(
            1, [ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=5))]
        )

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(StorageObjectRemovedEvent(object_uid=1))

        assert self.storage().get_item_by_gid(1, 100) is None

    def test_storage_objects_removed_event_removes_multiple_items(self):
        self.game_state.guild_chest.tab_number = 1
        self.storage().set_tab_content(
            1,
            [
                ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=5)),
                ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=3)),
            ],
        )

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(StorageObjectsRemovedEvent(objects_uid=[1, 2]))

        assert self.storage().get_item_by_gid(1, 100) is None
        assert self.storage().get_item_by_gid(1, 200) is None

    def test_remove_item_by_uid_removes_matching_item_and_leaves_others(self):
        self.storage().set_tab_content(
            1,
            [
                ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=5)),
                ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=3)),
            ],
        )

        self.storage().remove_item_by_uid(1, 2)

        assert self.storage().get_item_by_gid(1, 200) is None
        assert self.storage().get_item_by_gid(1, 100) is not None

    def test_set_item_creates_tab_and_stores_item_by_gid(self):
        self.storage().set_item(
            2, ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=3))
        )

        stored_item = self.storage().get_item_by_gid(2, 200)
        assert stored_item is not None
        assert stored_item.item.uid == 2
        assert stored_item.item.quantity == 3

    def test_get_available_quantity_subtracts_reservations(self):
        self.storage().set_tab_content(
            1, [ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))]
        )

        self.storage().reserve_quantity(1, 100, 4, "BotA")
        self.storage().reserve_quantity(1, 100, 3, "BotB")

        assert self.storage().get_available_quantity(1, 100) == 3

    def test_get_storage_objects_by_gid_returns_available_quantity_copy(self):
        self.storage().set_tab_content(
            1,
            [
                ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10)),
                ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=2)),
            ],
        )
        self.storage().reserve_quantity(1, 100, 4, "BotA")
        self.storage().reserve_quantity(1, 200, 2, "BotB")

        storage_objects = self.storage().get_storage_objects_by_gid()

        assert storage_objects[100].item.quantity == 6
        assert storage_objects[100] is not self.storage().get_item_by_gid(1, 100)
        assert 200 not in storage_objects
        assert self.storage().get_item_by_gid(1, 100).item.quantity == 10  # type: ignore[union-attr]

    def test_get_storage_objects_by_gid_returns_detached_copies(self):
        self.storage().set_tab_content(
            1,
            [ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))],
        )

        storage_objects = self.storage().get_storage_objects_by_gid()
        storage_objects[100].item.quantity = 1

        assert self.storage().get_item_by_gid(1, 100).item.quantity == 10  # type: ignore[union-attr]

    def test_release_reservation_restores_available_quantity(self):
        self.storage().set_tab_content(
            1, [ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))]
        )
        self.storage().reserve_quantity(1, 100, 4, "BotA")

        self.storage().release_reservation(1, 100, 4, "BotA")

        assert self.storage().get_available_quantity(1, 100) == 10

    def test_clear_all_reservations_for_bot_removes_only_target_bot(self):
        self.storage().set_tab_content(
            1, [ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))]
        )
        self.storage().set_tab_content(
            2, [ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=10))]
        )
        self.storage().reserve_quantity(1, 100, 4, "BotA")
        self.storage().reserve_quantity(1, 100, 2, "BotB")
        self.storage().reserve_quantity(2, 200, 3, "BotA")

        self.storage().clear_all_reservations_for_bot("BotA")

        assert self.storage().get_available_quantity(1, 100) == 8
        assert self.storage().get_available_quantity(2, 200) == 10

    def test_can_access_guild_chest_requires_sub_and_guild(self):
        self.game_state.guild_chest.has_guild = False

        assert self.game_state.guild_chest.can_access_guild_chest is False

        self.game_state.guild_chest.has_guild = True
        assert self.game_state.guild_chest.can_access_guild_chest is False

    def test_multiple_tabs_storage(self):
        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(
            StorageInventoryContentEvent(
                objects=[ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))]
            )
        )

        assert self.storage().get_item_by_gid(1, 100) is not None

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=2, storage_max_slot=100))
        self.inject(
            StorageInventoryContentEvent(
                objects=[ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=20))]
            )
        )

        assert self.storage().get_item_by_gid(1, 100) is not None
        assert self.storage().get_item_by_gid(2, 200) is not None

    def test_two_bots_same_server_share_guild_chest_updates_on_same_tab(self):
        other_bot = self.create_other_bot("OtherBotGuildChest", TEST_SERVER_ID)

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(
            StorageInventoryContentEvent(
                objects=[ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))]
            )
        )

        other_bot.event_manager.process_msg(
            ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100)
        )
        other_bot.event_manager.process_msg(
            StorageObjectUpdateEvent(
                object=ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=6))
            )
        )

        item = self.storage().get_item_by_gid(1, 100)
        assert item is not None
        assert item.item.quantity == 6
        assert self.game_state.guild_chest.tab_number == 1
        assert other_bot.game_state.guild_chest.tab_number == 1

    def test_two_bots_same_server_keep_independent_local_tab_numbers(self):
        other_bot = self.create_other_bot("OtherBotGuildTabs", TEST_SERVER_ID)

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(
            StorageInventoryContentEvent(
                objects=[ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))]
            )
        )

        other_bot.event_manager.process_msg(
            ExchangeStartedWithMultiTabStorageEvent(tab_number=2, storage_max_slot=100)
        )
        other_bot.event_manager.process_msg(
            StorageInventoryContentEvent(
                objects=[ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=20))]
            )
        )

        assert self.game_state.guild_chest.tab_number == 1
        assert other_bot.game_state.guild_chest.tab_number == 2
        assert self.storage().get_item_by_gid(1, 100) is not None
        assert self.storage().get_item_by_gid(2, 200) is not None

    def test_two_bots_same_server_share_removal_on_same_tab(self):
        other_bot = self.create_other_bot("OtherBotGuildRemove", TEST_SERVER_ID)

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(
            StorageInventoryContentEvent(
                objects=[ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))]
            )
        )

        other_bot.event_manager.process_msg(
            ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100)
        )
        other_bot.event_manager.process_msg(StorageObjectRemovedEvent(object_uid=1))

        assert self.storage().get_item_by_gid(1, 100) is None

    def test_two_bots_different_servers_do_not_share_guild_chest_state(self):
        other_server_id = 2
        other_bot = self.create_other_bot("OtherBotGuildIsolation", other_server_id)

        self.inject(ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100))
        self.inject(
            StorageInventoryContentEvent(
                objects=[ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))]
            )
        )

        other_bot.event_manager.process_msg(
            ExchangeStartedWithMultiTabStorageEvent(tab_number=1, storage_max_slot=100)
        )
        other_bot.event_manager.process_msg(
            StorageInventoryContentEvent(
                objects=[ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=7))]
            )
        )

        assert self.storage(TEST_SERVER_ID).get_item_by_gid(1, 100) is not None
        assert self.storage(TEST_SERVER_ID).get_item_by_gid(1, 200) is None
        assert self.storage(other_server_id).get_item_by_gid(1, 200) is not None
        assert self.storage(other_server_id).get_item_by_gid(1, 100) is None
