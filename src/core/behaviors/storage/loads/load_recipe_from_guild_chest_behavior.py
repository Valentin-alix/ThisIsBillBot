from dataclasses import dataclass, field

from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMoveRequest,
)
from d3_mapping.resources.protos.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
    GuildChestTabSelectRequest,
)
from d3_mapping.resources.protos.game.inventory_pb2 import InventoryWeightEvent
from models.datas.recipe_root import RecipeItem

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.storage.consts import GUILD_CONTENT_BY_TAB, USEFUL_UNLOAD
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config.timings import BASE_RANGE, SMALL_RANGE
from src.core.logic.craft.craft import (
    get_max_possible_result_quantity,
    get_max_result_quantity,
)
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB


@dataclass
class IngredientsInfo:
    gid: int
    quantity: int
    tab: int


@dataclass
class LoadRecipeFromGuildChestBehavior(Behavior):
    enter_guild_chest_behavior: EnterGuildChestBehavior
    unload_behavior: UnloadBehavior

    _remaining_recipes: list[RecipeItem] = field(init=False, default_factory=list)
    _loaded_recipes_infos: list[tuple[RecipeItem, int]] = field(
        init=False, default_factory=list
    )

    def run(self, recipes: list[RecipeItem]) -> None:
        self._remaining_recipes = recipes.copy()
        self._loaded_recipes_infos = []
        if self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:
            return self.unload_behavior.start(
                callback=self.on_unload_behavior_finished,
                parent=self,
            )
        self.on_unloaded()

    def on_unload_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            self.logger.error(error_code)
            return self.finish(
                error_code=error_code,
                loaded_recipes_infos=self._loaded_recipes_infos,
                remaining_recipes=self._remaining_recipes,
            )
        self.on_unloaded()

    def on_unloaded(self):
        self.run_timer(
            BASE_RANGE,
            lambda: self.enter_guild_chest_behavior.start(
                callback=self.on_entered_guild_chest_behavior,
                parent=self,
            ),
        )

    def on_entered_guild_chest_behavior(self, error_code: str | None):
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
            for tab, item_gids in GUILD_CONTENT_BY_TAB.items()
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
        return self.run_timer(
            SMALL_RANGE,
            lambda: self.event_manager.send(GuildChestTabSelectRequest(tab_number=tab)),
        )

    def load_recipe(self):
        if len(self._remaining_recipes) == 0:
            return self.on_full_loaded()

        recipe = self._remaining_recipes.pop()
        objects_by_gid = {
            gid: object
            for object_by_gid in CHEST_OBJECT_BY_GID_BY_TAB.values()
            for gid, object in object_by_gid.items()
        }
        max_result_quantity, weight_for_one_result = get_max_result_quantity(
            self.logger, objects_by_gid, recipe
        )
        if max_result_quantity == 0:
            # not enough ingredients in chest
            self._remaining_recipes.remove(recipe)
            return self.load_recipe()

        max_possible_result_quantity = get_max_possible_result_quantity(
            self.game_state.inventory.weight_max,
            self.game_state.inventory.inventory_weight,
            weight_for_one_result,
            max_result_quantity,
        )
        if max_possible_result_quantity == 0:
            return self.on_full_loaded()

        self._loaded_recipes_infos.append((recipe, max_possible_result_quantity))
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
        # sort by tab to avoid useless comeback
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
        req = ExchangeObjectMoveRequest(
            object_uid=CHEST_OBJECT_BY_GID_BY_TAB[
                self.game_state.guild_chest.tab_number
            ][ingredient_info.gid].item.uid,
            quantity=-ingredient_info.quantity * max_possible_result_quantity,
        )
        self.run_timer(SMALL_RANGE, lambda: self.event_manager.send(req))

    def on_ingredient_loaded(
        self,
        ingredients_infos: list[IngredientsInfo],
        max_possible_result_quantity: int,
    ):
        self.load_ingredient(ingredients_infos, max_possible_result_quantity)

    def on_full_loaded(self):
        self.event_manager.on(
            ExchangeLeaveEvent,
            callback=lambda _: self.finish(
                remaining_recipes=self._remaining_recipes,
                loaded_recipes_infos=self._loaded_recipes_infos,
            ),
            originator=self,
            once=True,
        )
        self.run_timer(BASE_RANGE, self.leave_all_dialogs)

    def leave_all_dialogs(self):
        request = DialogLeaveRequest()
        self.event_manager.send(request)
        self.event_manager.send(request)
