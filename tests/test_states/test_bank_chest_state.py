from datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory
from datas.protos.non_obf.game.exchange_pb2 import ExchangeStartedWithStorageEvent
from datas.protos.non_obf.game.inventory_pb2 import (
    StorageInventoryContentEvent,
    StorageObjectUpdateEvent,
)

from tests.test_states.state_test_base import StateTestBase

BANK_STORAGE_MAX_SLOT = 100_000


class TestBankChestState(StateTestBase):
    def open_bank(self) -> None:
        self.inject(
            ExchangeStartedWithStorageEvent(storage_max_slot=BANK_STORAGE_MAX_SLOT)
        )

    def test_storage_inventory_content_event_sets_bank_by_gid(self):
        self.open_bank()
        self.inject(
            StorageInventoryContentEvent(
                objects=[
                    ObjectItemInventory(item=ObjectItem(uid=10, gid=400, quantity=254)),
                ]
            )
        )

        assert 400 in self.game_state.inventory.bank_object_by_gid
        assert self.game_state.inventory.bank_object_by_gid[400].item.quantity == 254

    def test_storage_object_update_event_uses_gid_as_key(self):
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

        assert 400 in self.game_state.inventory.bank_object_by_gid
        assert self.game_state.inventory.bank_object_by_gid[400].item.quantity == 4
        assert 10 not in self.game_state.inventory.bank_object_by_gid

    def test_storage_object_update_event_does_not_leave_stale_gid_entry(self):
        """Regression: uid was used as key, leaving the gid entry with the old quantity."""
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

        assert self.game_state.inventory.bank_object_by_gid[400].item.quantity == 4
