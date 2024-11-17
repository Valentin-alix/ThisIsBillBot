import unittest
from unittest.mock import MagicMock, patch

from D3Database.enums.jobs_enum import JobEnum
from D3Database.models.datas.recipe_root import RecipeItem
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.engine.crafts.recipes import FORBIDDEN_CRAFT_IDS
from tests.test_behaviors.behavior_test_base import BehaviorTestBase


class TestCraftBehavior(BehaviorTestBase):
    def setUp(self):
        super().setUp()

        # Use MagicMock for all complex dependencies
        self.behavior = CraftBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
            auto_trip_smart_behavior=MagicMock(),
            load_recipe_behavior=MagicMock(),
            interactive_behavior=MagicMock(),
            pathfinding=MagicMock(),
        )

    def test_run_with_empty_recipes(self):
        # Mock get_valid_recipes to return empty list
        with patch.object(self.game_state.craft, "get_valid_recipes", return_value=[]):
            self.start_behavior(self.behavior, recipes=[])

            assert self.wait_for_callback(timeout=1.0)
            self.assert_callback_success()

    def test_run_filters_forbidden_crafts(self):
        # Create a forbidden recipe
        forbidden_id = next(iter(FORBIDDEN_CRAFT_IDS))
        forbidden_recipe = RecipeItem(
            resultId=forbidden_id,
            resultNameId="1",
            resultTypeId=0,
            resultLevel=1,
            ingredientIds=[],
            quantities=[],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        # Mock get_valid_recipes to filter it out
        with patch.object(self.game_state.craft, "get_valid_recipes", return_value=[]):
            self.start_behavior(self.behavior, recipes=[forbidden_recipe])

            assert self.wait_for_callback(timeout=1.0)
            self.assert_callback_success()

    def test_process_remaining_recipes_with_stop_condition(self):
        recipe1 = RecipeItem(
            resultId=100,
            resultNameId="100",
            resultTypeId=0,
            resultLevel=1,
            ingredientIds=[],
            quantities=[],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        recipe2 = RecipeItem(
            resultId=200,
            resultNameId="200",
            resultTypeId=0,
            resultLevel=5,
            ingredientIds=[],
            quantities=[],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        # Stop condition: only craft recipes with resultLevel < 3
        def stop_condition(recipe: RecipeItem) -> bool:
            return recipe.resultLevel >= 3

        with patch.object(
            self.game_state.craft, "get_valid_recipes", return_value=[recipe1, recipe2]
        ):
            self.start_behavior(
                self.behavior,
                recipes=[recipe1, recipe2],
                stop_craft_recipe_condition=stop_condition,
            )

            # Should filter recipe2 because resultLevel=5 >= 3
            assert len(self.behavior._remaining_recipes) == 1
            assert self.behavior._remaining_recipes[0].resultId == 100

    def test_craft_timeout_adds_to_forbidden_list(self):
        gid = 999

        # Trigger timeout
        self.behavior.on_timeout_exchange_ready(gid)

        # Should add to forbidden list
        assert gid in FORBIDDEN_CRAFT_IDS

        # Cleanup
        FORBIDDEN_CRAFT_IDS.discard(gid)

    def test_stop_condition_filters_recipes(self):
        recipe1 = RecipeItem(
            resultId=100,
            resultNameId="100",
            resultTypeId=0,
            resultLevel=1,
            ingredientIds=[],
            quantities=[],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        recipe2 = RecipeItem(
            resultId=200,
            resultNameId="200",
            resultTypeId=0,
            resultLevel=10,
            ingredientIds=[],
            quantities=[],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        # Set stop condition
        def stop_condition(recipe: RecipeItem) -> bool:
            return recipe.resultLevel > 5

        self.behavior._stop_craft_recipe_condition = stop_condition
        self.behavior._remaining_recipes = [recipe1, recipe2]

        # Process remaining recipes
        self.behavior.process_remaining_recipes()

        # Only recipe1 should remain (recipe2 filtered by stop condition)
        assert len(self.behavior._remaining_recipes) == 1
        assert self.behavior._remaining_recipes[0].resultId == 100


if __name__ == "__main__":
    unittest.main()
