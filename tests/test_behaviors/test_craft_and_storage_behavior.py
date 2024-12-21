from collections.abc import Callable
from types import SimpleNamespace
from unittest.mock import patch

from datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory
from datas.protos.non_obf.game.exchange_pb2 import ExchangeCraftStartedEvent
from dofus_unity_reader.models.datas.recipe_root import RecipeItem

from src.core.behaviors.craft.craft_behavior import LoadedRecipeInfo
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.storage.loads.load_item_request import LoadItemInfo
from tests.test_states.state_test_base import StateTestBase


def _run_immediately(
    range_time: tuple[float, float] | float,
    func: Callable[[], None],
) -> None:
    del range_time
    func()


def _finish_enter_behavior(
    callback: Callable[..., None] | None,
    parent: object | None,
    *args: object,
    **kwargs: object,
) -> None:
    del parent, args, kwargs
    if callback is not None:
        callback(None)


class TestCraftAndStorageBehavior(StateTestBase):
    def setUp(self) -> None:
        super().setUp()
        self.sale_hotel_behavior = next(
            behavior
            for behavior in self.bot.usable_behaviors
            if isinstance(behavior, SaleHotelPricesBehavior)
        )

    def _build_recipe(self, result_id: int, result_name_id: str, skill_id: int) -> RecipeItem:
        return RecipeItem(
            resultId=result_id,
            resultNameId=result_name_id,
            resultTypeId=0,
            resultLevel=1,
            ingredientIds=[],
            quantities=[],
            jobId=1,
            skillId=skill_id,
        )

    def test_craft_behavior_does_not_mutate_loaded_recipe_input(self) -> None:
        first_recipe = self._build_recipe(1001, "1", 42)
        second_recipe = self._build_recipe(1002, "2", 42)
        recipes_infos = [
            LoadedRecipeInfo(recipe=first_recipe, quantity=3),
            LoadedRecipeInfo(recipe=second_recipe, quantity=4),
        ]
        craft_behavior = self.bot.craft_behavior

        with (
            patch.object(craft_behavior, "send_message_delayed"),
            patch.object(craft_behavior.event_manager, "on"),
            patch(
                "src.core.behaviors.craft.craft_behavior.I18N",
                return_value=SimpleNamespace(name_by_id={1: "First", 2: "Second"}),
            ),
        ):
            craft_behavior.on_exchange_craft_started_event(
                ExchangeCraftStartedEvent(),
                recipes_infos,
            )

        assert recipes_infos == [
            LoadedRecipeInfo(recipe=first_recipe, quantity=3),
            LoadedRecipeInfo(recipe=second_recipe, quantity=4),
        ]

    def test_load_from_bank_behavior_does_not_mutate_input_requests(self) -> None:
        load_from_bank_behavior = self.sale_hotel_behavior.load_from_bank_behavior
        self.game_state.inventory.weight_max = 1000
        self.game_state.inventory.inventory_weight = 0
        self.game_state.inventory.bank_object_by_gid[303] = ObjectItemInventory(
            item=ObjectItem(uid=1, gid=303, quantity=150)
        )
        request = LoadItemInfo(item_gid=303, remaining_quantity=150, tab=0)

        with (
            patch.object(
                load_from_bank_behavior,
                "run_timer",
                side_effect=_run_immediately,
            ),
            patch.object(load_from_bank_behavior, "send_message_delayed"),
            patch.object(load_from_bank_behavior.event_manager, "on"),
            patch.object(
                load_from_bank_behavior.enter_bank_behavior,
                "start",
                side_effect=_finish_enter_behavior,
            ),
        ):
            load_from_bank_behavior.run([request])

        assert request == LoadItemInfo(item_gid=303, remaining_quantity=150, tab=0)

    def test_load_from_guild_chest_behavior_does_not_mutate_input_requests(self) -> None:
        load_from_guild_chest_behavior = (
            self.sale_hotel_behavior.load_from_guild_chest_behavior
        )
        self.game_state.inventory.weight_max = 1000
        self.game_state.inventory.inventory_weight = 0
        self.game_state.guild_chest.tab_number = 1
        self.game_state.guild_chest.storage.set_tab_content(
            1,
            [ObjectItemInventory(item=ObjectItem(uid=1, gid=303, quantity=150))],
        )
        request = LoadItemInfo(item_gid=303, remaining_quantity=150, tab=1)

        with (
            patch.object(
                load_from_guild_chest_behavior,
                "run_timer",
                side_effect=_run_immediately,
            ),
            patch.object(load_from_guild_chest_behavior, "send_message_delayed"),
            patch.object(load_from_guild_chest_behavior.event_manager, "on"),
            patch.object(
                load_from_guild_chest_behavior.enter_guild_chest_behavior,
                "start",
                side_effect=_finish_enter_behavior,
            ),
        ):
            load_from_guild_chest_behavior.run([request])

        assert request == LoadItemInfo(item_gid=303, remaining_quantity=150, tab=1)

    def test_abort_current_recipe_releases_guild_chest_reservations(self) -> None:
        load_recipe_behavior = (
            self.bot.craft_behavior.load_recipe_behavior.load_recipe_from_guild_chest_behavior
        )
        self.game_state.guild_chest.storage.set_tab_content(
            1,
            [ObjectItemInventory(item=ObjectItem(uid=1, gid=303, quantity=10))],
        )
        recipe = RecipeItem(
            resultId=999,
            resultNameId="999",
            resultTypeId=0,
            resultLevel=1,
            ingredientIds=[303],
            quantities=[2],
            jobId=1,
            skillId=1,
        )
        load_recipe_behavior._remaining_recipes = [recipe]
        load_recipe_behavior._loaded_recipes_infos = [(recipe, 3)]

        with patch.object(load_recipe_behavior, "load_recipe"):
            load_recipe_behavior.reserve_ingredients_for_recipe(recipe, 3)

            assert self.game_state.guild_chest.storage.get_available_quantity(1, 303) == 4

            load_recipe_behavior.abort_current_recipe()

        assert self.game_state.guild_chest.storage.get_available_quantity(1, 303) == 10
        assert recipe not in load_recipe_behavior._remaining_recipes
