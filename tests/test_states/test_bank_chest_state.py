from datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory
from datas.protos.non_obf.game.exchange_pb2 import ExchangeStartedWithStorageEvent
from datas.protos.non_obf.game.inventory_pb2 import (
    StorageInventoryContentEvent,
    StorageObjectsRemovedEvent,
    StorageObjectUpdateEvent,
)

from tests.test_states.state_test_base import StateTestBase

BANK_STORAGE_MAX_SLOT = 100_000


class TestBankChestState(StateTestBase):
    def open_bank(self) -> None:
        self.inject(
            ExchangeStartedWithStorageEvent(storage_max_slot=BANK_STORAGE_MAX_SLOT)
        )

    def test_storage_inventory_content_event_sets_bank_by_uid(self):
        self.open_bank()
        self.inject(
            StorageInventoryContentEvent(
                objects=[
                    ObjectItemInventory(item=ObjectItem(uid=10, gid=400, quantity=254)),
                ]
            )
        )

        assert 10 in self.game_state.inventory.bank_objects_by_uid
        assert self.game_state.inventory.bank_objects_by_uid[10].item.quantity == 254
        assert (
            self.game_state.inventory.get_bank_objects_by_gid()[400].item.quantity
            == 254
        )

    def test_storage_object_update_event_uses_uid_as_key(self):
        self.open_bank()
        self.inject(
            StorageInventoryContentEvent(
                objects=[
                    ObjectItemInventory(item=ObjectItem(uid=10, gid=400, quantity=254)),
                ]
            )
        )

        self.inject(
            StorageObjectUpdateEvent(
                object=ObjectItemInventory(item=ObjectItem(uid=10, gid=400, quantity=4))
            )
        )

        assert 10 in self.game_state.inventory.bank_objects_by_uid
        assert self.game_state.inventory.bank_objects_by_uid[10].item.quantity == 4
        assert 400 not in self.game_state.inventory.bank_objects_by_uid

    def test_storage_object_update_event_updates_gid_view(self):
        self.open_bank()
        self.inject(
            StorageInventoryContentEvent(
                objects=[
                    ObjectItemInventory(item=ObjectItem(uid=10, gid=400, quantity=254)),
                ]
            )
        )

        self.inject(
            StorageObjectUpdateEvent(
                object=ObjectItemInventory(item=ObjectItem(uid=10, gid=400, quantity=4))
            )
        )

        assert (
            self.game_state.inventory.get_bank_objects_by_gid()[400].item.quantity == 4
        )

    def test_storage_objects_removed_event_removes_duplicate_gid_by_uid(self):
        self.open_bank()
        self.inject(
            StorageInventoryContentEvent(
                objects=[
                    ObjectItemInventory(item=ObjectItem(uid=10, gid=400, quantity=254)),
                    ObjectItemInventory(item=ObjectItem(uid=11, gid=400, quantity=4)),
                ]
            )
        )

        self.inject(StorageObjectsRemovedEvent(objects_uid=[10]))

        assert 10 not in self.game_state.inventory.bank_objects_by_uid
        assert 11 in self.game_state.inventory.bank_objects_by_uid
        assert (
            self.game_state.inventory.get_bank_objects_by_gid()[400].item.quantity == 4
        )

    def test_storage_objects_removed_event_handles_multiple_duplicate_gid_uids(self):
        self.open_bank()
        self.inject(
            StorageInventoryContentEvent(
                objects=[
                    ObjectItemInventory(item=ObjectItem(uid=10, gid=400, quantity=254)),
                    ObjectItemInventory(item=ObjectItem(uid=11, gid=400, quantity=4)),
                    ObjectItemInventory(item=ObjectItem(uid=12, gid=401, quantity=8)),
                ]
            )
        )

        self.inject(StorageObjectsRemovedEvent(objects_uid=[10, 11]))

        assert 10 not in self.game_state.inventory.bank_objects_by_uid
        assert 11 not in self.game_state.inventory.bank_objects_by_uid
        assert 12 in self.game_state.inventory.bank_objects_by_uid
        assert 400 not in self.game_state.inventory.get_bank_objects_by_gid()
