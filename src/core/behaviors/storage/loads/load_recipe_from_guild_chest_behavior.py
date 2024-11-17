from dataclasses import dataclass

from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeObjectMoveRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
    GuildChestTabSelectRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.behaviors.storage.loads.recipe_loader_behavior import (
    RecipeLoaderBehavior,
)
from src.core.config import SMALL_RANGE
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB, GIDS_BY_TAB


@dataclass
class IngredientsInfo:
    gid: int
    quantity: int
    tab: int


@dataclass
class LoadRecipeFromGuildChestBehavior(RecipeLoaderBehavior):
    enter_guild_chest_behavior: EnterGuildChestBehavior

    def enter_storage(self) -> None:
        self.enter_guild_chest_behavior.start(
            callback=self.on_entered_storage,
            parent=self,
        )

    def on_entered_storage(self, error_code: str | None):
        if error_code is not None:
            self.logger.error(error_code)
            return self.finish(
                error_code=error_code,
                loaded_recipes_infos=self._loaded_recipes_infos,
                remaining_recipes=self._remaining_recipes,
            )

        all_ingredient_ids: set[int] = {
            ingredient_id
            for recipe in self._remaining_recipes
            for ingredient_id in recipe.ingredientIds
        }
        tab_to_discovers = {
            tab
            for tab, item_gids in GIDS_BY_TAB.items()
            if any(
                ingredient_id in item_gids and tab not in CHEST_OBJECT_BY_GID_BY_TAB
                for ingredient_id in all_ingredient_ids
            )
        }
        self.logger.info(f"Tabs to discover : {tab_to_discovers}")
        self.discover_tabs(tab_to_discovers)

    def discover_tabs(self, tabs: set[int]):
        if len(tabs) == 0:
            return self.load_recipe()

        self.event_manager.on(
            GuildChestCurrentListenersAddEvent,
            lambda _: self.discover_tabs(tabs),
            once=True,
            originator=self,
        )
        tab = tabs.pop()
        self.logger.info(f"Gonna discover tab {tab}")
        return self.send_message_delayed(
            GuildChestTabSelectRequest(tab_number=tab),
            SMALL_RANGE,
        )

    def get_storage_objects_by_gid(self) -> dict:
        return {
            gid: object
            for object_by_gid in CHEST_OBJECT_BY_GID_BY_TAB.values()
            for gid, object in object_by_gid.items()
        }

    def load_ingredients_for_recipe(
        self, recipe, max_possible_result_quantity: int
    ) -> None:
        ingredients_infos: list[IngredientsInfo] = [
            IngredientsInfo(
                gid=ingredient_id,
                quantity=quantity,
                tab=next(
                    tab
                    for tab, item_gids in CHEST_OBJECT_BY_GID_BY_TAB.items()
                    if ingredient_id in item_gids
                ),
            )
            for ingredient_id, quantity in zip(recipe.ingredientIds, recipe.quantities)
        ]
        ingredients_infos.sort(
            key=lambda ingredient_info: (
                ingredient_info.tab == self.game_state.guild_chest.tab_number,
                ingredient_info.tab,
            )
        )
        self.load_ingredient(
            ingredients_infos=ingredients_infos,
            max_possible_result_quantity=max_possible_result_quantity,
        )

    def load_ingredient(
        self,
        ingredients_infos: list[IngredientsInfo],
        max_possible_result_quantity: int,
    ):
        if len(ingredients_infos) == 0:
            return self.load_recipe()

        ingredient_info = ingredients_infos.pop()
        if self.game_state.guild_chest.tab_number != ingredient_info.tab:
            self.event_manager.on(
                GuildChestCurrentListenersAddEvent,
                lambda _: self.on_tab_of_item_to_load(
                    ingredient_info, ingredients_infos, max_possible_result_quantity
                ),
                once=True,
                originator=self,
            )
            return self.run_timer(
                SMALL_RANGE,
                lambda: self.event_manager.send(
                    GuildChestTabSelectRequest(tab_number=ingredient_info.tab)
                ),
            )
        self.on_tab_of_item_to_load(
            ingredient_info, ingredients_infos, max_possible_result_quantity
        )

    def on_tab_of_item_to_load(
        self,
        ingredient_info: IngredientsInfo,
        ingredients_infos: list[IngredientsInfo],
        max_possible_result_quantity: int,
    ):
        self.event_manager.on(
            InventoryWeightEvent,
            callback=lambda _: self.on_ingredient_loaded(
                ingredients_infos, max_possible_result_quantity
            ),
            originator=self,
            once=True,
        )
        self.logger.info(f"Current tab : {self.game_state.guild_chest.tab_number}")
        self.logger.info(f"Tab of item {ingredient_info.tab}")
        req = ExchangeObjectMoveRequest(
            object_uid=CHEST_OBJECT_BY_GID_BY_TAB[
                self.game_state.guild_chest.tab_number
            ][ingredient_info.gid].item.uid,
            quantity=-ingredient_info.quantity * max_possible_result_quantity,
        )
        self.send_message_delayed(req, SMALL_RANGE)

    def on_ingredient_loaded(
        self,
        ingredients_infos: list[IngredientsInfo],
        max_possible_result_quantity: int,
    ):
        self.load_ingredient(ingredients_infos, max_possible_result_quantity)
