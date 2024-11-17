from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    ObjectItem,
    ObjectItemInventory,
    ObjectUidWithQuantity,
)
from D3Mapping.d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveUseRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    ObjectAddedEvent,
    ObjectQuantityEvent,
)
from tests.test_states.state_test_base import StateTestBase


class TestStatsFrame(StateTestBase):
    def setUp(self):
        super().setUp()
        self.resource_harvested_calls = []

        def track_signal(gid, quantity):
            self.resource_harvested_calls.append((gid, quantity))

        self.game_state.player.game_info_signals.resource_harvested.connect(
            track_signal
        )

    def test_object_added_after_interactive_use(self):
        """Test that ObjectAddedEvent after InteractiveUseRequest emits resource_harvested."""
        # Setup: Use interactive element
        self.inject(InteractiveUseRequest(element_id=123, skill_instance_uid=456))

        # Add a new object (harvested resource) - using real GID 44
        new_obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=44, quantity=5))
        self.inject(ObjectAddedEvent(object=new_obj))

        # Verify signal was emitted with correct values
        assert len(self.resource_harvested_calls) == 1
        assert self.resource_harvested_calls[0] == (44, 5)

    def test_object_quantity_increased_after_interactive_use(self):
        """Test that ObjectQuantityEvent after InteractiveUseRequest emits resource_harvested."""
        # Setup: Add existing object to inventory
        existing_obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=44, quantity=10))
        self.game_state.inventory.add_object(existing_obj)

        # Use interactive element
        self.inject(InteractiveUseRequest(element_id=123, skill_instance_uid=456))

        # Increase quantity
        self.inject(
            ObjectQuantityEvent(object=ObjectUidWithQuantity(object_uid=1, quantity=15))
        )

        # Verify signal was emitted with the difference (15 - 10 = 5)
        assert len(self.resource_harvested_calls) == 1
        assert self.resource_harvested_calls[0] == (44, 5)

    def test_object_added_without_interactive_use_does_nothing(self):
        """Test that ObjectAddedEvent without InteractiveUseRequest doesn't emit signal."""
        # Add object without using interactive element first
        new_obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=44, quantity=5))
        self.inject(ObjectAddedEvent(object=new_obj))

        # Verify signal was NOT emitted
        assert len(self.resource_harvested_calls) == 0

    def test_object_quantity_without_interactive_use_does_nothing(self):
        """Test that ObjectQuantityEvent without InteractiveUseRequest doesn't emit signal."""
        # Setup: Add existing object
        existing_obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=44, quantity=10))
        self.game_state.inventory.add_object(existing_obj)

        # Increase quantity without interactive use
        self.inject(
            ObjectQuantityEvent(object=ObjectUidWithQuantity(object_uid=1, quantity=15))
        )

        # Verify signal was NOT emitted
        assert len(self.resource_harvested_calls) == 0

    def test_multiple_interactive_uses_track_separately(self):
        """Test that each interactive use tracks its own quantity changes."""
        # Setup: Add object with initial quantity
        existing_obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=44, quantity=10))
        self.game_state.inventory.add_object(existing_obj)

        # First harvest
        self.inject(InteractiveUseRequest(element_id=123, skill_instance_uid=456))
        self.inject(
            ObjectQuantityEvent(object=ObjectUidWithQuantity(object_uid=1, quantity=15))
        )

        # Verify first harvest (15 - 10 = 5)
        assert len(self.resource_harvested_calls) == 1
        assert self.resource_harvested_calls[0] == (44, 5)

        # Clear calls for next harvest
        self.resource_harvested_calls.clear()

        # Second harvest (now starting from 15)
        self.inject(InteractiveUseRequest(element_id=123, skill_instance_uid=456))
        self.inject(
            ObjectQuantityEvent(object=ObjectUidWithQuantity(object_uid=1, quantity=22))
        )

        # Verify second harvest (22 - 15 = 7)
        assert len(self.resource_harvested_calls) == 1
        assert self.resource_harvested_calls[0] == (44, 7)

    def test_object_quantity_decrease_does_not_emit(self):
        """Test that quantity decreases don't emit resource_harvested."""
        # Setup: Add object
        existing_obj = ObjectItemInventory(item=ObjectItem(uid=1, gid=44, quantity=10))
        self.game_state.inventory.add_object(existing_obj)

        # Use interactive (shouldn't matter, decrease shouldn't emit)
        self.inject(InteractiveUseRequest(element_id=123, skill_instance_uid=456))

        # Decrease quantity
        self.inject(
            ObjectQuantityEvent(object=ObjectUidWithQuantity(object_uid=1, quantity=5))
        )

        # Verify signal was NOT emitted for decrease
        assert len(self.resource_harvested_calls) == 0

    def test_new_object_after_interactive_use(self):
        """Test harvesting a completely new resource."""
        # Use interactive element
        self.inject(InteractiveUseRequest(element_id=123, skill_instance_uid=456))

        # Add new object that didn't exist before - using real GID 49
        new_obj = ObjectItemInventory(item=ObjectItem(uid=10, gid=49, quantity=3))
        self.inject(ObjectAddedEvent(object=new_obj))

        # Verify signal emitted with full quantity
        assert len(self.resource_harvested_calls) == 1
        assert self.resource_harvested_calls[0] == (49, 3)
