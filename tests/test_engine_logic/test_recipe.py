import unittest

from D3Database.data_center.data_reader import DataReader
from D3Database.enums.jobs_enum import JobEnum
from D3Database.models.datas.recipe_root import RecipeItem
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    ObjectItem,
    ObjectItemInventory,
)
from src.core.engine.crafts.recipes import (
    FORBIDDEN_CRAFT_IDS,
    get_max_possible_result_quantity,
    get_max_result_quantity,
    get_valid_recipes,
    is_not_valid_recipe_for_lvl_up_job,
)
from src.core.signals.log_signals import LogSignals
from src.services.logging.logger import Logger


class TestRecipesReal(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(LogSignals(), "test")
        self.jobs_lvl_by_id: dict[int, int] = {JobEnum.PEASANT: 1, JobEnum.ALCHEMIST: 5}

    # ------------------------------------------------------------------
    # is_not_valid_recipe_for_lvl_up_job
    # ------------------------------------------------------------------
    def test_is_not_valid_recipe_for_lvl_up_job(self):
        recipe = RecipeItem(
            resultId=1,
            resultNameId="1",
            resultTypeId=0,
            resultLevel=5,
            ingredientIds=[],
            quantities=[2],
            jobId=JobEnum.PEASANT,
            skillId=101,
        )
        result = is_not_valid_recipe_for_lvl_up_job(
            recipe, is_sub=False, jobs_lvl_by_id=self.jobs_lvl_by_id
        )
        self.assertFalse(result)

        result2 = is_not_valid_recipe_for_lvl_up_job(
            recipe, is_sub=False, jobs_lvl_by_id={JobEnum.PEASANT: 200}
        )
        self.assertTrue(result2)

    # ------------------------------------------------------------------
    # get_max_result_quantity
    # ------------------------------------------------------------------
    def test_get_max_result_quantity(self):
        item1 = ObjectItem(uid=1, gid=1, quantity=10)
        item2 = ObjectItem(uid=2, gid=2, quantity=4)
        inventory = {
            1: ObjectItemInventory(item=item1),
            2: ObjectItemInventory(item=item2),
        }

        recipe = RecipeItem(
            resultId=1,
            resultNameId="1",
            resultTypeId=0,
            resultLevel=1,
            ingredientIds=[1, 2],
            quantities=[2, 1],
            jobId=1,
            skillId=1,
        )

        max_q, weight = get_max_result_quantity(self.logger, inventory, recipe)
        self.assertEqual(max_q, 4)  # limité par ingredient 2
        # Poids calculé via DataReader().item_by_id[].realWeight
        expected_weight = sum(
            qty * (DataReader().item_by_id[gid].realWeight or 0)
            for gid, qty in zip(recipe.ingredientIds, recipe.quantities)
        )
        self.assertEqual(weight, expected_weight)

    # ------------------------------------------------------------------
    # get_max_possible_result_quantity
    # ------------------------------------------------------------------
    def test_get_max_possible_result_quantity(self):
        result = get_max_possible_result_quantity(
            weight_max=100,
            inventory_weight=60,
            weight_for_one_result=5,
            max_result_quantity=10,
        )
        self.assertEqual(result, 8)

    # ------------------------------------------------------------------
    # get_valid_recipes
    # ------------------------------------------------------------------
    def test_get_valid_recipes(self):
        # Recette interdite
        forbidden_id = next(iter(FORBIDDEN_CRAFT_IDS))
        forbidden_recipe = RecipeItem(
            resultId=forbidden_id,
            resultNameId="1",
            resultTypeId=0,
            resultLevel=1,
            ingredientIds=[],
            quantities=[],
            jobId=1,
            skillId=1,
        )
        valid = get_valid_recipes(self.logger, self.jobs_lvl_by_id, [forbidden_recipe])
        self.assertEqual(valid, [])

        # Recette valide
        valid_recipe = RecipeItem(
            resultId=2,
            resultNameId="2",
            resultTypeId=0,
            resultLevel=5,
            ingredientIds=[],
            quantities=[],
            jobId=1,
            skillId=1,
        )
        valid2 = get_valid_recipes(self.logger, self.jobs_lvl_by_id, [valid_recipe])
        self.assertEqual(valid2, [valid_recipe])


if __name__ == "__main__":
    unittest.main()
