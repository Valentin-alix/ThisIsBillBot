from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeStartedWithMultiTabStorageEvent,
)
from datas.protos.non_obf.game.guild_member_pb2 import (
    GuildMembershipEvent,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    MultiTabStorageEvent,
    StorageInventoryContentEvent,
    StorageObjectRemovedEvent,
    StorageObjectsRemovedEvent,
    StorageObjectsUpdateEvent,
    StorageObjectUpdateEvent,
    StorageTab,
)

from src.core.bot.bot import Bot
from src.core.states.guild_chest_storage import GuildChestStorage
from tests.fixtures.inventory import make_inventory_item


class TestGuildChestState:
    def test_guild_membership_event_sets_has_guild(
        self,
        runtime_bot: Bot,
    ):
        assert runtime_bot.game_state.guild_chest.has_guild is False

        runtime_bot.event_manager.process_msg(GuildMembershipEvent())

        assert runtime_bot.game_state.guild_chest.has_guild is True

    def test_exchange_started_with_multi_tab_storage_sets_tab_number(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            ExchangeStartedWithMultiTabStorageEvent(
                tab_number=2,
                storage_max_slot=100,
            )
        )

        assert runtime_bot.game_state.guild_chest.tab_number == 2

    def test_exchange_started_with_tab_number_100_uses_storage_max_slot(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            ExchangeStartedWithMultiTabStorageEvent(
                tab_number=100,
                storage_max_slot=5,
            )
        )

        assert runtime_bot.game_state.guild_chest.tab_number == 5

    def test_multi_tab_storage_event_sets_available_tabs(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            MultiTabStorageEvent(
                tabs=[
                    StorageTab(tab_number=2),
                    StorageTab(tab_number=4),
                ]
            )
        )

        assert runtime_bot.game_state.guild_chest.tabs == [2, 4]

    def test_storage_inventory_content_event_populates_current_tab(
        self,
        runtime_bot: Bot,
        guild_chest_storage: GuildChestStorage,
    ):
        self._open_tab(runtime_bot)

        runtime_bot.event_manager.process_msg(
            StorageInventoryContentEvent(
                objects=[
                    make_inventory_item(
                        uid=1,
                        gid=100,
                        quantity=10,
                    ),
                    make_inventory_item(
                        uid=2,
                        gid=200,
                        quantity=5,
                    ),
                ]
            )
        )

        assert guild_chest_storage.get_item_by_gid(1, 100) is not None
        assert guild_chest_storage.get_item_by_gid(1, 200) is not None
        assert guild_chest_storage.get_item_by_gid(1, 100).item.quantity == 10  # type: ignore[union-attr]

    def test_storage_object_update_event_updates_current_tab_item(
        self,
        runtime_bot: Bot,
        guild_chest_storage: GuildChestStorage,
    ):
        guild_chest_storage.set_tab_content(
            1,
            [
                make_inventory_item(
                    uid=1,
                    gid=100,
                    quantity=5,
                )
            ],
        )
        self._open_tab(runtime_bot)

        runtime_bot.event_manager.process_msg(
            StorageObjectUpdateEvent(
                object=make_inventory_item(
                    uid=1,
                    gid=100,
                    quantity=8,
                )
            )
        )

        item = guild_chest_storage.get_item_by_gid(1, 100)
        assert item is not None
        assert item.item.quantity == 8

    def test_storage_objects_update_event_updates_and_adds_current_tab_items(
        self,
        runtime_bot: Bot,
        guild_chest_storage: GuildChestStorage,
    ):
        guild_chest_storage.set_tab_content(
            1,
            [
                make_inventory_item(
                    uid=1,
                    gid=100,
                    quantity=5,
                )
            ],
        )
        self._open_tab(runtime_bot)

        runtime_bot.event_manager.process_msg(
            StorageObjectsUpdateEvent(
                objects=[
                    make_inventory_item(
                        uid=1,
                        gid=100,
                        quantity=9,
                    ),
                    make_inventory_item(
                        uid=2,
                        gid=200,
                        quantity=4,
                    ),
                ]
            )
        )

        item_100 = guild_chest_storage.get_item_by_gid(1, 100)
        item_200 = guild_chest_storage.get_item_by_gid(1, 200)

        assert item_100 is not None
        assert item_100.item.quantity == 9
        assert item_200 is not None
        assert item_200.item.quantity == 4

    def test_storage_object_removed_event_removes_current_tab_item(
        self,
        runtime_bot: Bot,
        guild_chest_storage: GuildChestStorage,
    ):
        guild_chest_storage.set_tab_content(
            1,
            [
                make_inventory_item(
                    uid=1,
                    gid=100,
                    quantity=5,
                )
            ],
        )
        self._open_tab(runtime_bot)

        runtime_bot.event_manager.process_msg(StorageObjectRemovedEvent(object_uid=1))

        assert guild_chest_storage.get_item_by_gid(1, 100) is None

    def test_storage_objects_removed_event_removes_current_tab_items(
        self,
        runtime_bot: Bot,
        guild_chest_storage: GuildChestStorage,
    ):
        guild_chest_storage.set_tab_content(
            1,
            [
                make_inventory_item(
                    uid=1,
                    gid=100,
                    quantity=5,
                ),
                make_inventory_item(
                    uid=2,
                    gid=200,
                    quantity=3,
                ),
            ],
        )
        self._open_tab(runtime_bot)

        runtime_bot.event_manager.process_msg(
            StorageObjectsRemovedEvent(objects_uid=[1, 2])
        )

        assert guild_chest_storage.get_item_by_gid(1, 100) is None
        assert guild_chest_storage.get_item_by_gid(1, 200) is None

    def test_can_access_guild_chest_requires_sub_and_guild(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.guild_chest.has_guild = False

        assert runtime_bot.game_state.guild_chest.can_access_guild_chest is False

        runtime_bot.game_state.guild_chest.has_guild = True

        assert runtime_bot.game_state.guild_chest.can_access_guild_chest is False

    def _open_tab(
        self,
        runtime_bot: Bot,
        tab_number: int = 1,
    ) -> None:
        runtime_bot.event_manager.process_msg(
            ExchangeStartedWithMultiTabStorageEvent(
                tab_number=tab_number,
                storage_max_slot=100,
            )
        )
