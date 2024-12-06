from datas.protos.non_obf.game.common_pb2 import (
    ObjectItem,
    ObjectItemInventory,
)
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeCraftCountRequest,
    ExchangeCraftStartedEvent,
    ExchangeLeaveEvent,
    ExchangeReadyRequest,
    ExchangeSetCraftRecipeRequest,
)
from tests.test_states.state_test_base import StateTestBase


class TestCraftFrame(StateTestBase):
    def test_craft_single_item_consumes_ingredients(self):
        """Test crafting 1 item consumes the correct ingredients."""
        # Setup: Add ingredients to inventory
        # Using recipe 49: ingredientIds=[1673, 377], quantities=[1, 3]
        ingredient_1 = ObjectItemInventory(
            item=ObjectItem(uid=1, gid=1673, quantity=10)
        )
        ingredient_2 = ObjectItemInventory(item=ObjectItem(uid=2, gid=377, quantity=10))
        self.game_state.inventory.add_object(ingredient_1)
        self.game_state.inventory.add_object(ingredient_2)

        # Start craft exchange
        self.inject(ExchangeCraftStartedEvent())

        # Select recipe 49
        self.inject(ExchangeSetCraftRecipeRequest(object_uid=49))

        # Set craft count to 1 (default, may not receive this event)
        # The frame defaults to _craft_count=1

        # Complete craft
        self.inject(ExchangeReadyRequest())

        # Verify ingredients were consumed (1 and 3)
        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 9
        assert self.game_state.inventory.objects_by_uid[2].item.quantity == 7

    def test_craft_multiple_items_consumes_correct_amounts(self):
        """Test crafting multiple items consumes the correct total ingredients."""
        # Setup: Add ingredients to inventory
        # Using recipe 49: ingredientIds=[1673, 377], quantities=[1, 3]
        ingredient_1 = ObjectItemInventory(
            item=ObjectItem(uid=1, gid=1673, quantity=20)
        )
        ingredient_2 = ObjectItemInventory(item=ObjectItem(uid=2, gid=377, quantity=20))
        self.game_state.inventory.add_object(ingredient_1)
        self.game_state.inventory.add_object(ingredient_2)

        # Start craft exchange
        self.inject(ExchangeCraftStartedEvent())

        # Select recipe 49
        self.inject(ExchangeSetCraftRecipeRequest(object_uid=49))

        # Set craft count to 5
        self.inject(ExchangeCraftCountRequest(count=5))

        # Complete craft
        self.inject(ExchangeReadyRequest())

        # Verify ingredients were consumed (5*1=5, 5*3=15)
        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 15
        assert self.game_state.inventory.objects_by_uid[2].item.quantity == 5

    def test_craft_removes_ingredient_when_quantity_reaches_zero(self):
        """Test that ingredients are removed from inventory when quantity reaches 0."""
        # Setup: Add exact amount of ingredients needed
        # Using recipe 49: ingredientIds=[1673, 377], quantities=[1, 3]
        ingredient_1 = ObjectItemInventory(item=ObjectItem(uid=1, gid=1673, quantity=3))
        ingredient_2 = ObjectItemInventory(item=ObjectItem(uid=2, gid=377, quantity=9))
        self.game_state.inventory.add_object(ingredient_1)
        self.game_state.inventory.add_object(ingredient_2)

        # Start craft exchange
        self.inject(ExchangeCraftStartedEvent())

        # Select recipe 49
        self.inject(ExchangeSetCraftRecipeRequest(object_uid=49))

        # Set craft count to 3 (consumes 3*1=3 and 3*3=9)
        self.inject(ExchangeCraftCountRequest(count=3))

        # Complete craft
        self.inject(ExchangeReadyRequest())

        # Verify ingredients were removed
        assert 1 not in self.game_state.inventory.objects_by_uid
        assert 2 not in self.game_state.inventory.objects_by_uid

    def test_craft_with_multiple_quantity_ingredients(self):
        """Test crafting with recipe requiring multiple quantities of ingredients."""
        # Using recipe 55: ingredientIds=[364, 300, 2659], quantities=[4, 4, 4]
        ingredient_1 = ObjectItemInventory(item=ObjectItem(uid=1, gid=364, quantity=20))
        ingredient_2 = ObjectItemInventory(item=ObjectItem(uid=2, gid=300, quantity=20))
        ingredient_3 = ObjectItemInventory(
            item=ObjectItem(uid=3, gid=2659, quantity=20)
        )
        self.game_state.inventory.add_object(ingredient_1)
        self.game_state.inventory.add_object(ingredient_2)
        self.game_state.inventory.add_object(ingredient_3)

        # Start craft exchange
        self.inject(ExchangeCraftStartedEvent())

        # Select recipe 55
        self.inject(ExchangeSetCraftRecipeRequest(object_uid=55))

        # Craft 3 times
        self.inject(ExchangeCraftCountRequest(count=3))

        # Complete craft
        self.inject(ExchangeReadyRequest())

        # Verify ingredients consumed: 4*3=12 for each
        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 8
        assert self.game_state.inventory.objects_by_uid[2].item.quantity == 8
        assert self.game_state.inventory.objects_by_uid[3].item.quantity == 8

    def test_exchange_leave_clears_craft_state(self):
        """Test that leaving craft exchange clears the frame state."""
        # Setup
        ingredient_1 = ObjectItemInventory(
            item=ObjectItem(uid=1, gid=1673, quantity=10)
        )
        self.game_state.inventory.add_object(ingredient_1)

        # Start craft
        self.inject(ExchangeCraftStartedEvent())
        self.inject(ExchangeSetCraftRecipeRequest(object_uid=49))
        self.inject(ExchangeCraftCountRequest(count=5))

        # Leave without completing
        self.inject(ExchangeLeaveEvent())

        # Verify state was cleared (no consumption should happen)
        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 10

    def test_craft_multiple_recipes_in_sequence(self):
        """Test crafting multiple different recipes in sequence."""
        # Setup: Add ingredients for both recipes
        # Recipe 49: ingredientIds=[1673, 377], quantities=[1, 3]
        # Recipe 44: ingredientIds=[16512, 303], quantities=[3, 3]
        ingredient_1673 = ObjectItemInventory(
            item=ObjectItem(uid=1, gid=1673, quantity=20)
        )
        ingredient_377 = ObjectItemInventory(
            item=ObjectItem(uid=2, gid=377, quantity=20)
        )
        ingredient_16512 = ObjectItemInventory(
            item=ObjectItem(uid=3, gid=16512, quantity=20)
        )
        ingredient_303 = ObjectItemInventory(
            item=ObjectItem(uid=4, gid=303, quantity=20)
        )
        self.game_state.inventory.add_object(ingredient_1673)
        self.game_state.inventory.add_object(ingredient_377)
        self.game_state.inventory.add_object(ingredient_16512)
        self.game_state.inventory.add_object(ingredient_303)

        # First craft: Recipe 49 x2
        self.inject(ExchangeCraftStartedEvent())
        self.inject(ExchangeSetCraftRecipeRequest(object_uid=49))
        self.inject(ExchangeCraftCountRequest(count=2))
        self.inject(ExchangeReadyRequest())

        # Verify first craft consumption (2*1=2, 2*3=6)
        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 18  # 1673
        assert self.game_state.inventory.objects_by_uid[2].item.quantity == 14  # 377

        # Second craft: Recipe 44 x3
        self.inject(ExchangeSetCraftRecipeRequest(object_uid=44))
        self.inject(ExchangeCraftCountRequest(count=3))
        self.inject(ExchangeReadyRequest())

        # Verify second craft consumption (3*3=9, 3*3=9)
        assert self.game_state.inventory.objects_by_uid[3].item.quantity == 11  # 16512
        assert self.game_state.inventory.objects_by_uid[4].item.quantity == 11  # 303

        # Leave craft
        self.inject(ExchangeLeaveEvent())

    def test_exchange_ready_without_recipe_does_nothing(self):
        """Test that ExchangeReadyRequest without a recipe doesn't crash."""
        ingredient_1 = ObjectItemInventory(item=ObjectItem(uid=1, gid=303, quantity=10))
        self.game_state.inventory.add_object(ingredient_1)

        # Inject ready request without selecting a recipe
        self.inject(ExchangeReadyRequest())

        # Verify nothing changed
        assert self.game_state.inventory.objects_by_uid[1].item.quantity == 10
