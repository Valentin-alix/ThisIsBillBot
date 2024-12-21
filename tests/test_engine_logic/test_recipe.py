import unittest
from unittest.mock import MagicMock, patch

from dofus_unity_reader.enums.jobs_enum import JobEnum
from dofus_unity_reader.models.datas.recipe_root import RecipeItem
from datas.protos.non_obf.game.common_pb2 import (
    ObjectItem,
    ObjectItemInventory,
)
from src.core.engine.crafts.recipes import (
    get_benefice_on_craft_recipe,
    get_max_possible_result_quantity,
    get_max_result_quantity,
    get_valid_recipes,
    is_not_valid_recipe_for_lvl_up_job_or_benefice,
)
from src.core.signals.log_signals import LogSignals
from src.services.logging.logger import Logger


class TestRecipesReal(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = Logger(LogSignals(), "test")
        self.jobs_lvl_by_id: dict[int, int] = {JobEnum.PEASANT: 1, JobEnum.ALCHEMIST: 5}

    def tearDown(self) -> None:
        self.logger.close()

    # ------------------------------------------------------------------
    # is_not_valid_recipe_for_lvl_up_job
    # ------------------------------------------------------------------
    def test_is_not_valid_recipe_for_lvl_up_job(self) -> None:
        # Use a real Peasant level 1 recipe with gatherable ingredients.
        recipe = RecipeItem(
            resultId=468,
            resultNameId="521785",
            resultTypeId=33,
            resultLevel=1,
            ingredientIds=[289],
            quantities=[4],
            jobId=JobEnum.PEASANT,
            skillId=27,
        )
        result = is_not_valid_recipe_for_lvl_up_job_or_benefice(
            recipe, is_sub=False, jobs_lvl_by_id=self.jobs_lvl_by_id
        )
        self.assertFalse(result)

        result2 = is_not_valid_recipe_for_lvl_up_job_or_benefice(
            recipe, is_sub=False, jobs_lvl_by_id={JobEnum.PEASANT: 200}
        )
        self.assertTrue(result2)

    # ------------------------------------------------------------------
    # get_max_result_quantity
    # ------------------------------------------------------------------
    def test_get_max_result_quantity(self) -> None:
        # Use real item GIDs: 44 (weight=1), 49 (weight=5).
        item1 = ObjectItem(uid=1, gid=44, quantity=10)
        item2 = ObjectItem(uid=2, gid=49, quantity=4)
        inventory = {
            44: ObjectItemInventory(item=item1),
            49: ObjectItemInventory(item=item2),
        }

        recipe = RecipeItem(
            resultId=100,
            resultNameId="100",
            resultTypeId=0,
            resultLevel=1,
            ingredientIds=[44, 49],
            quantities=[2, 1],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        max_q, weight = get_max_result_quantity(self.logger, inventory, recipe)
        assert max_q == 4  # limité par ingredient 49 (quantity=4, needs 1 per craft)
        # Poids calculé: 2*1 + 1*5 = 7
        expected_weight = 2 * 1 + 1 * 5
        assert weight == expected_weight

    # ------------------------------------------------------------------
    # get_max_possible_result_quantity
    # ------------------------------------------------------------------
    def test_get_max_possible_result_quantity(self) -> None:
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
    def test_get_valid_recipes(self) -> None:
        forbidden_craft_ids: set[int] = {60}

        # Recette interdite
        forbidden_recipe = RecipeItem(
            resultId=60,
            resultNameId="1",
            resultTypeId=0,
            resultLevel=1,
            ingredientIds=[],
            quantities=[],
            jobId=JobEnum.WOODCUTTER,
            skillId=6,  # Valid skill ID with parent job WOODCUTTER (2)
        )
        valid = get_valid_recipes(
            self.logger, self.jobs_lvl_by_id, [forbidden_recipe], forbidden_craft_ids
        )
        assert valid == []

        # Recette valide pour ALCHEMIST (niveau 5)
        valid_recipe = RecipeItem(
            resultId=2,
            resultNameId="2",
            resultTypeId=0,
            resultLevel=5,
            ingredientIds=[],
            quantities=[],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,  # Valid skill ID for ALCHEMIST
        )
        valid2 = get_valid_recipes(
            self.logger, self.jobs_lvl_by_id, [valid_recipe], set()
        )
        assert valid2 == [valid_recipe]

        # Recette invalide car le niveau du job est insuffisant
        invalid_recipe = RecipeItem(
            resultId=3,
            resultNameId="3",
            resultTypeId=0,
            resultLevel=10,  # Niveau 10 requis mais ALCHEMIST est niveau 5
            ingredientIds=[],
            quantities=[],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )
        valid3 = get_valid_recipes(
            self.logger, self.jobs_lvl_by_id, [invalid_recipe], set()
        )
        assert valid3 == []

    # ------------------------------------------------------------------
    # get_benefice_on_craft_recipe
    # ------------------------------------------------------------------
    @patch("src.core.engine.crafts.recipes.SaleHotelController")
    def test_get_benefice_on_craft_recipe_profitable(
        self, mock_controller_class: MagicMock
    ):
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.get_avg_price_by_gid.return_value = {
            100: 1000.0,
            50: 200.0,
            51: 150.0,
        }

        recipe = RecipeItem(
            resultId=100,
            resultNameId="100",
            resultTypeId=0,
            resultLevel=10,
            ingredientIds=[50, 51],
            quantities=[2, 3],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        profit, profit_percent = get_benefice_on_craft_recipe(recipe)

        expected_profit = 1000.0 - 200.0 - 150.0
        expected_percent = expected_profit / 1000.0

        self.assertEqual(profit, expected_profit)
        self.assertAlmostEqual(profit_percent, expected_percent)
        self.assertEqual(profit, 650.0)
        self.assertAlmostEqual(profit_percent, 0.65)

    @patch("src.core.engine.crafts.recipes.SaleHotelController")
    def test_get_benefice_on_craft_recipe_loss(self, mock_controller_class: MagicMock):
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.get_avg_price_by_gid.return_value = {
            100: 500.0,
            50: 300.0,
            51: 250.0,
        }

        recipe = RecipeItem(
            resultId=100,
            resultNameId="100",
            resultTypeId=0,
            resultLevel=10,
            ingredientIds=[50, 51],
            quantities=[2, 3],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        profit, profit_percent = get_benefice_on_craft_recipe(recipe)

        expected_profit = 500.0 - 300.0 - 250.0
        expected_percent = expected_profit / 500.0

        self.assertEqual(profit, expected_profit)
        self.assertAlmostEqual(profit_percent, expected_percent)
        self.assertEqual(profit, -50.0)
        self.assertAlmostEqual(profit_percent, -0.1)

    @patch("src.core.engine.crafts.recipes.SaleHotelController")
    def test_get_benefice_on_craft_recipe_no_result_price(
        self, mock_controller_class: MagicMock
    ):
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.get_avg_price_by_gid.return_value = {
            50: 200.0,
            51: 150.0,
        }

        recipe = RecipeItem(
            resultId=100,
            resultNameId="100",
            resultTypeId=0,
            resultLevel=10,
            ingredientIds=[50, 51],
            quantities=[2, 3],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        profit, profit_percent = get_benefice_on_craft_recipe(recipe)

        self.assertEqual(profit, 0)
        self.assertEqual(profit_percent, 0)

    @patch("src.core.engine.crafts.recipes.SaleHotelController")
    def test_get_benefice_on_craft_recipe_missing_ingredient_price(
        self, mock_controller_class: MagicMock
    ):
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.get_avg_price_by_gid.return_value = {
            100: 1000.0,
            50: 200.0,
        }

        recipe = RecipeItem(
            resultId=100,
            resultNameId="100",
            resultTypeId=0,
            resultLevel=10,
            ingredientIds=[50, 51],
            quantities=[2, 3],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        profit, profit_percent = get_benefice_on_craft_recipe(recipe)

        self.assertEqual(profit, 0)
        self.assertEqual(profit_percent, 0)

    @patch("src.core.engine.crafts.recipes.SaleHotelController")
    def test_get_benefice_on_craft_recipe_zero_profit(
        self, mock_controller_class: MagicMock
    ):
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.get_avg_price_by_gid.return_value = {
            100: 500.0,
            50: 300.0,
            51: 200.0,
        }

        recipe = RecipeItem(
            resultId=100,
            resultNameId="100",
            resultTypeId=0,
            resultLevel=10,
            ingredientIds=[50, 51],
            quantities=[2, 3],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        profit, profit_percent = get_benefice_on_craft_recipe(recipe)

        expected_profit = 500.0 - 300.0 - 200.0
        expected_percent = expected_profit / 500.0

        self.assertEqual(profit, expected_profit)
        self.assertAlmostEqual(profit_percent, expected_percent)
        self.assertEqual(profit, 0.0)
        self.assertAlmostEqual(profit_percent, 0.0)

    @patch("src.core.engine.crafts.recipes.SaleHotelController")
    def test_get_benefice_on_craft_recipe_single_ingredient(
        self, mock_controller_class: MagicMock
    ):
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.get_avg_price_by_gid.return_value = {
            100: 800.0,
            50: 300.0,
        }

        recipe = RecipeItem(
            resultId=100,
            resultNameId="100",
            resultTypeId=0,
            resultLevel=5,
            ingredientIds=[50],
            quantities=[1],
            jobId=JobEnum.PEASANT,
            skillId=27,
        )

        profit, profit_percent = get_benefice_on_craft_recipe(recipe)

        expected_profit = 800.0 - 300.0
        expected_percent = expected_profit / 800.0

        self.assertEqual(profit, expected_profit)
        self.assertAlmostEqual(profit_percent, expected_percent)
        self.assertEqual(profit, 500.0)
        self.assertAlmostEqual(profit_percent, 0.625)

    @patch("src.core.engine.crafts.recipes.SaleHotelController")
    def test_get_benefice_on_craft_recipe_multiple_ingredients(
        self, mock_controller_class: MagicMock
    ):
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.get_avg_price_by_gid.return_value = {
            200: 2000.0,
            10: 100.0,
            20: 150.0,
            30: 200.0,
            40: 250.0,
        }

        recipe = RecipeItem(
            resultId=200,
            resultNameId="200",
            resultTypeId=0,
            resultLevel=50,
            ingredientIds=[10, 20, 30, 40],
            quantities=[1, 2, 3, 4],
            jobId=JobEnum.ALCHEMIST,
            skillId=23,
        )

        profit, profit_percent = get_benefice_on_craft_recipe(recipe)

        expected_profit = 2000.0 - 100.0 - 150.0 - 200.0 - 250.0
        expected_percent = expected_profit / 2000.0

        self.assertEqual(profit, expected_profit)
        self.assertAlmostEqual(profit_percent, expected_percent)
        self.assertEqual(profit, 1300.0)
        self.assertAlmostEqual(profit_percent, 0.65)


if __name__ == "__main__":
    unittest.main()
