from unittest.mock import MagicMock

import pytest
from datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory
from dofus_unity_reader.game_constants.job import JobEnum
from dofus_unity_reader.models.datas.recipe_root import RecipeItem

from src.core.engine.crafts.recipes import (
    get_benefice_on_craft_recipe,
    get_max_possible_result_quantity,
    get_max_result_quantity,
    get_valid_recipes,
    is_not_valid_recipe_for_lvl_up_job_or_benefice,
)
from src.services.logging_utils.loggers import BotLogger
from tests.fixtures.data import make_recipe

_CASE_MAKE_RECIPE: list[tuple[RecipeItem, set[int], bool]] = [
    (
        make_recipe(
            result_id=60,
            result_level=1,
            ingredient_ids=[],
            quantities=[],
            job_id=JobEnum.WOODCUTTER,
            skill_id=6,
        ),
        {60},
        False,
    ),
    (
        make_recipe(
            result_id=2,
            result_level=5,
            ingredient_ids=[],
            quantities=[],
            job_id=JobEnum.ALCHEMIST,
            skill_id=23,
        ),
        set(),
        True,
    ),
    (
        make_recipe(
            result_id=3,
            result_level=10,
            ingredient_ids=[],
            quantities=[],
            job_id=JobEnum.ALCHEMIST,
            skill_id=23,
        ),
        set(),
        False,
    ),
]


class TestRecipes:
    def test_is_not_validmake_recipe_for_lvl_up_job(
        self,
    ) -> None:
        recipe = make_recipe(
            result_id=468,
            result_level=1,
            ingredient_ids=[289],
            quantities=[4],
            job_id=JobEnum.PEASANT,
            skill_id=27,
        )

        assert not is_not_valid_recipe_for_lvl_up_job_or_benefice(
            recipe,
            is_sub=False,
            jobs_lvl_by_id={JobEnum.PEASANT: 1, JobEnum.ALCHEMIST: 5},
        )
        assert is_not_valid_recipe_for_lvl_up_job_or_benefice(
            recipe,
            is_sub=False,
            jobs_lvl_by_id={JobEnum.PEASANT: 200},
        )

    def test_get_max_result_quantity(
        self,
        logger: BotLogger,
    ) -> None:
        inventory = {
            44: ObjectItemInventory(item=ObjectItem(uid=1, gid=44, quantity=10)),
            49: ObjectItemInventory(item=ObjectItem(uid=2, gid=49, quantity=4)),
        }

        recipe = make_recipe(
            result_id=100,
            result_level=1,
            ingredient_ids=[44, 49],
            quantities=[2, 1],
            job_id=JobEnum.ALCHEMIST,
            skill_id=23,
        )

        max_quantity, weight = get_max_result_quantity(logger, inventory, recipe)

        assert max_quantity == 4
        assert weight == 7

    def test_get_max_possible_result_quantity(
        self,
    ) -> None:
        assert (
            get_max_possible_result_quantity(
                weight_max=100,
                inventory_weight=60,
                weight_for_one_result=5,
                max_result_quantity=10,
            )
            == 8
        )

    @pytest.mark.parametrize(
        ("recipe", "forbidden_result_ids", "is_valid"), _CASE_MAKE_RECIPE
    )
    def test_get_valid_recipe(
        self,
        logger: BotLogger,
        recipe: RecipeItem,
        forbidden_result_ids: set[int],
        is_valid: bool,
    ) -> None:
        result = get_valid_recipes(
            logger,
            {JobEnum.PEASANT: 1, JobEnum.ALCHEMIST: 5},
            [recipe],
            forbidden_result_ids,
        )

        assert result == ([recipe] if is_valid else [])

    @pytest.mark.parametrize(
        (
            "prices_by_gid",
            "recipe",
            "expected_profit",
            "expected_profit_percent",
        ),
        [
            (
                {100: 1000.0, 50: 200.0, 51: 150.0},
                make_recipe(ingredient_ids=[50, 51], quantities=[2, 3]),
                650.0,
                0.65,
            ),
            (
                {100: 500.0, 50: 300.0, 51: 250.0},
                make_recipe(ingredient_ids=[50, 51], quantities=[2, 3]),
                -50.0,
                -0.1,
            ),
            (
                {50: 200.0, 51: 150.0},
                make_recipe(ingredient_ids=[50, 51], quantities=[2, 3]),
                0.0,
                0.0,
            ),
            (
                {100: 1000.0, 50: 200.0},
                make_recipe(ingredient_ids=[50, 51], quantities=[2, 3]),
                0.0,
                0.0,
            ),
            (
                {100: 500.0, 50: 300.0, 51: 200.0},
                make_recipe(ingredient_ids=[50, 51], quantities=[1, 1]),
                0.0,
                0.0,
            ),
            (
                {100: 800.0, 50: 300.0},
                make_recipe(
                    result_id=100,
                    result_level=5,
                    ingredient_ids=[50],
                    quantities=[1],
                    job_id=JobEnum.PEASANT,
                    skill_id=27,
                ),
                500.0,
                0.625,
            ),
            (
                {200: 2000.0, 10: 100.0, 20: 150.0, 30: 200.0, 40: 250.0},
                make_recipe(
                    result_id=200,
                    result_level=50,
                    ingredient_ids=[10, 20, 30, 40],
                    quantities=[1, 2, 3, 4],
                ),
                1300.0,
                0.65,
            ),
        ],
    )
    def test_get_benefice_on_craftmake_recipe(
        self,
        monkeypatch: pytest.MonkeyPatch,
        prices_by_gid: dict[int, float],
        recipe: RecipeItem,
        expected_profit: float,
        expected_profit_percent: float,
    ) -> None:
        mock_controller = MagicMock()
        mock_controller.get_avg_price_by_gid.return_value = prices_by_gid

        monkeypatch.setattr(
            "src.core.engine.crafts.recipes.SaleHotelController",
            MagicMock(return_value=mock_controller),
        )

        profit, profit_percent = get_benefice_on_craft_recipe(recipe)

        assert profit == expected_profit
        assert profit_percent == pytest.approx(expected_profit_percent)  # pyright: ignore[reportUnknownMemberType]
