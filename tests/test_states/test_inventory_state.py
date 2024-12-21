from datas.protos.non_obf.game.common_pb2 import (
    ObjectItem,
    ObjectItemInventory,
    ObjectUidWithQuantity,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryContentEvent,
    InventoryWeightEvent,
    KamasUpdateEvent,
    ObjectAddedEvent,
    ObjectDeletedEvent,
    ObjectModifiedEvent,
    ObjectQuantityEvent,
    ObjectsAddedEvent,
    ObjectsDeletedEvent,
    ObjectsQuantityEvent,
)
from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals
from tests.test_states.state_test_base import StateTestBase, TEST_ACCOUNT


class TestInventoryState(StateTestBase):
    def test_initial_state(self):
        assert self.game_state.inventory.kamas == 500_000
        assert self.game_state.inventory.inventory_weight == 0
        assert self.game_state.inventory.weight_max == 1
        assert len(self.game_state.inventory.objects_by_uid) == 0

    def test_collection_fields_are_not_shared_between_instances(self):
        other_bot = BotFactory.create_bot(
            SharedSignals(), account=TEST_ACCOUNT, is_fake=True
        )

        assert (
            self.game_state.inventory.bank_object_by_gid
            is not other_bot.game_state.inventory.bank_object_by_gid
        )
        assert (
            self.game_state.inventory.objects_by_uid
            is not other_bot.game_state.inventory.objects_by_uid
        )

    def test_clear_state_resets_values(self):
        self.game_state.inventory.kamas = 1_000_000
        self.game_state.inventory.inventory_weight = 500
        self.game_state.inventory.weight_max = 1000
        obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))
        self.game_state.inventory.add_object(obj)

        self.game_state.inventory.clear_state()

        assert self.game_state.inventory.kamas == 0
        assert self.game_state.inventory.inventory_weight == 0
        assert self.game_state.inventory.weight_max == 1
        assert len(self.game_state.inventory.objects_by_uid) == 0

    def test_inventory_content_event_sets_objects_and_kamas(self):
        objects = [
            ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10)),
            ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=5)),
        ]
        msg = InventoryContentEvent(objects=objects, kamas=50000)

        self.inject(msg)

        assert len(self.game_state.inventory.objects_by_uid) == 2
        assert 1 in self.game_state.inventory.objects_by_uid
        assert 2 in self.game_state.inventory.objects_by_uid
        assert self.game_state.inventory.kamas == 50000

    def test_object_added_event_adds_object(self):
        obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))
        msg = ObjectAddedEvent(object=obj)

        self.inject(msg)

        assert 1 in self.game_state.inventory.objects_by_uid
        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 10

    def test_objects_added_event_adds_multiple_objects(self):
        self.inject(
            ObjectsAddedEvent(
                objects=[
                    ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10)),
                    ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=5)),
                ]
            )
        )

        assert set(self.game_state.inventory.objects_by_uid) == {1, 2}

    def test_object_deleted_event_removes_object(self):
        obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))
        self.game_state.inventory.add_object(obj)

        self.inject(ObjectDeletedEvent(object_uid=1))

        assert 1 not in self.game_state.inventory.objects_by_uid

    def test_objects_deleted_event_removes_multiple_objects(self):
        objects = [
            ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10)),
            ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=5)),
        ]
        self.game_state.inventory.add_objects(objects)

        self.inject(ObjectsDeletedEvent(objects_uid=[1, 2]))

        assert len(self.game_state.inventory.objects_by_uid) == 0

    def test_object_quantity_event_updates_quantity(self):
        obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))
        self.game_state.inventory.add_object(obj)

        msg = ObjectQuantityEvent(
            object=ObjectUidWithQuantity(object_uid=1, quantity=25)
        )

        self.inject(msg)

        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 25

    def test_objects_quantity_event_updates_multiple_quantities(self):
        self.game_state.inventory.add_objects(
            [
                ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10)),
                ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=5)),
            ]
        )

        self.inject(
            ObjectsQuantityEvent(
                object=[
                    ObjectUidWithQuantity(object_uid=1, quantity=12),
                    ObjectUidWithQuantity(object_uid=2, quantity=8),
                ]
            )
        )

        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 12
        assert self.game_state.inventory.objects_by_uid[2].item.quantity == 8

    def test_object_modified_event_replaces_object(self):
        self.game_state.inventory.add_object(
            ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))
        )

        self.inject(
            ObjectModifiedEvent(
                object=ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=99))
            )
        )

        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 99

    def test_inventory_weight_event_updates_weight(self):
        msg = InventoryWeightEvent(inventory_weight=500, weight_max=2000)

        self.inject(msg)

        assert self.game_state.inventory.inventory_weight == 500
        assert self.game_state.inventory.weight_max == 2000

    def test_pod_percentage_calculation(self):
        self.game_state.inventory.inventory_weight = 500
        self.game_state.inventory.weight_max = 1000

        assert self.game_state.inventory.pod_percentage == 0.5

    def test_is_full_pods_at_90_percent(self):
        self.game_state.inventory.inventory_weight = 900
        self.game_state.inventory.weight_max = 1000

        assert self.game_state.inventory.is_full_pods is True

    def test_is_full_pods_below_90_percent(self):
        self.game_state.inventory.inventory_weight = 899
        self.game_state.inventory.weight_max = 1000

        assert self.game_state.inventory.is_full_pods is False

    def test_kamas_update_event_sets_kamas(self):
        self.game_state.inventory.kamas = 1000

        self.inject(KamasUpdateEvent(quantity=700))

        assert self.game_state.inventory.kamas == 700

    def test_add_object_to_inventory(self):
        obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))

        self.game_state.inventory.add_object(obj)

        assert 1 in self.game_state.inventory.objects_by_uid
        assert self.game_state.inventory.objects_by_uid[1].item.gid == 100

    def test_add_objects_batch(self):
        objects = [
            ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10)),
            ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=5)),
        ]

        self.game_state.inventory.add_objects(objects)

        assert len(self.game_state.inventory.objects_by_uid) == 2
        assert 1 in self.game_state.inventory.objects_by_uid
        assert 2 in self.game_state.inventory.objects_by_uid

    def test_remove_object_from_inventory(self):
        obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))
        self.game_state.inventory.add_object(obj)

        self.game_state.inventory.remove_object(1)

        assert 1 not in self.game_state.inventory.objects_by_uid

    def test_remove_nonexistent_object_does_nothing(self):
        self.game_state.inventory.remove_object(999)

        assert 999 not in self.game_state.inventory.objects_by_uid

    def test_set_objects_replaces_existing(self):
        initial_obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))
        self.game_state.inventory.add_object(initial_obj)

        new_objects = [
            ObjectItemInventory(item=ObjectItem(uid=2, gid=200, quantity=5)),
        ]

        self.game_state.inventory.set_objects(new_objects)

        assert 1 not in self.game_state.inventory.objects_by_uid
        assert 2 in self.game_state.inventory.objects_by_uid

    def test_clear_inventory_method(self):
        obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=100, quantity=10))
        self.game_state.inventory.add_object(obj)

        self.game_state.inventory.clear_inventory()

        assert len(self.game_state.inventory.objects_by_uid) == 0
