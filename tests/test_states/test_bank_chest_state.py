from datas.protos.non_obf.game.exchange_pb2 import ExchangeStartedWithStorageEvent
from datas.protos.non_obf.game.inventory_pb2 import (
    StorageInventoryContentEvent,
    StorageObjectsRemovedEvent,
    StorageObjectUpdateEvent,
)

from src.core.bot.bot import Bot
from tests.fixtures.inventory import make_inventory_item

BANK_STORAGE_MAX_SLOT = 100_000


class TestBankChestState:
    def test_storage_inventory_content_event_sets_bank_objects(
        self,
        runtime_bot: Bot,
    ):
        self._open_bank(runtime_bot)

        runtime_bot.event_manager.process_msg(
            StorageInventoryContentEvent(
                objects=[
                    make_inventory_item(uid=10, gid=400, quantity=254),
                ]
            )
        )

        assert set(runtime_bot.game_state.inventory.bank_objects_by_uid) == {10}
        assert (
            runtime_bot.game_state.inventory.bank_objects_by_uid[10].item.quantity
            == 254
        )
        assert (
            runtime_bot.game_state.inventory.get_bank_objects_by_gid()[
                400
            ].item.quantity
            == 254
        )

    def test_storage_object_update_event_uses_uid_as_key_and_updates_gid_view(
        self,
        runtime_bot: Bot,
    ):
        self._open_bank(runtime_bot)

        runtime_bot.event_manager.process_msg(
            StorageInventoryContentEvent(
                objects=[
                    make_inventory_item(uid=10, gid=400, quantity=254),
                ]
            )
        )

        runtime_bot.event_manager.process_msg(
            StorageObjectUpdateEvent(
                object=make_inventory_item(uid=10, gid=400, quantity=4)
            )
        )

        assert set(runtime_bot.game_state.inventory.bank_objects_by_uid) == {10}
        assert (
            runtime_bot.game_state.inventory.bank_objects_by_uid[10].item.quantity == 4
        )
        assert 400 not in runtime_bot.game_state.inventory.bank_objects_by_uid
        assert (
            runtime_bot.game_state.inventory.get_bank_objects_by_gid()[
                400
            ].item.quantity
            == 4
        )

    def test_storage_objects_removed_event_keeps_gid_view_for_remaining_duplicate_uid(
        self,
        runtime_bot: Bot,
    ):
        self._open_bank(runtime_bot)

        runtime_bot.event_manager.process_msg(
            StorageInventoryContentEvent(
                objects=[
                    make_inventory_item(uid=10, gid=400, quantity=254),
                    make_inventory_item(uid=11, gid=400, quantity=4),
                ]
            )
        )

        runtime_bot.event_manager.process_msg(
            StorageObjectsRemovedEvent(objects_uid=[10])
        )

        assert set(runtime_bot.game_state.inventory.bank_objects_by_uid) == {11}
        assert (
            runtime_bot.game_state.inventory.get_bank_objects_by_gid()[
                400
            ].item.quantity
            == 4
        )

    def test_storage_objects_removed_event_removes_gid_view_when_last_uid_removed(
        self,
        runtime_bot: Bot,
    ):
        self._open_bank(runtime_bot)

        runtime_bot.event_manager.process_msg(
            StorageInventoryContentEvent(
                objects=[
                    make_inventory_item(uid=10, gid=400, quantity=254),
                    make_inventory_item(uid=11, gid=400, quantity=4),
                    make_inventory_item(uid=12, gid=401, quantity=8),
                ]
            )
        )

        runtime_bot.event_manager.process_msg(
            StorageObjectsRemovedEvent(objects_uid=[10, 11])
        )

        assert set(runtime_bot.game_state.inventory.bank_objects_by_uid) == {12}
        assert 400 not in runtime_bot.game_state.inventory.get_bank_objects_by_gid()

    def _open_bank(
        self,
        runtime_bot: Bot,
    ) -> None:
        runtime_bot.event_manager.process_msg(
            ExchangeStartedWithStorageEvent(storage_max_slot=BANK_STORAGE_MAX_SLOT)
        )
