from dataclasses import dataclass, field

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeObjectMoveRequest,
)
from datas.protos.non_obf.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
    GuildChestTabSelectRequest,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from dofus_unity_reader.models.datas.recipe_root import RecipeItem

from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.behaviors.storage.loads.recipe_loader_behavior import (
    RecipeLoaderBehavior,
)
from src.core.config import SMALL_RANGE
from src.core.states.guild_chest_state import GIDS_BY_TAB, GuildChestState


@dataclass
class IngredientsInfo:
    gid: int
    quantity: int
    tab: int


@dataclass
class LoadRecipeFromGuildChestBehavior(RecipeLoaderBehavior):
    enter_guild_chest_behavior: EnterGuildChestBehavior
    _current_recipe_being_loaded: RecipeItem | None = field(init=False, default=None)
    _current_recipe_quantity: int = field(init=False, default=0)

    def enter_storage(self) -> None:
        self.enter_guild_chest_behavior.start(
            callback=self.on_entered_storage,
            parent=self,
        )

    def on_entered_storage(self, error_code: str | None) -> None:
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
        server_id = self.game_state.player.server_id
        tab_to_discovers = {
            tab
            for tab, item_gids in GIDS_BY_TAB.items()
            if any(
                ingredient_id in item_gids
                and not GuildChestState.tab_exists(server_id, tab)
                for ingredient_id in all_ingredient_ids
            )
        }
        self.logger.info(f"Tabs to discover : {tab_to_discovers}")
        self.discover_tabs(tab_to_discovers)

    def discover_tabs(self, tabs: set[int]) -> None:
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

    def get_storage_objects_by_gid(self) -> dict[int, ObjectItemInventory]:
        return GuildChestState.get_storage_objects_by_gid(
            self.game_state.player.server_id
        )

    def reserve_ingredients_for_recipe(
        self, recipe: RecipeItem, max_possible_result_quantity: int
    ) -> None:
        self._current_recipe_being_loaded = recipe
        self._current_recipe_quantity = max_possible_result_quantity
        server_id = self.game_state.player.server_id
        for ingredient_id, quantity in zip(recipe.ingredientIds, recipe.quantities):
            tab = GuildChestState.get_tab_for_gid(server_id, ingredient_id)
            if tab is None:
                continue
            total_quantity = quantity * max_possible_result_quantity
            GuildChestState.reserve_quantity(
                server_id,
                tab,
                ingredient_id,
                total_quantity,
                self.game_state.player.character_name,
            )

    def load_ingredients_for_recipe(
        self, recipe: RecipeItem, max_possible_result_quantity: int
    ) -> None:
        server_id = self.game_state.player.server_id
        ingredients_infos: list[IngredientsInfo] = []
        for ingredient_id, quantity in zip(recipe.ingredientIds, recipe.quantities):
            tab = GuildChestState.get_tab_for_gid(server_id, ingredient_id)
            if tab is not None:
                ingredients_infos.append(
                    IngredientsInfo(
                        gid=ingredient_id,
                        quantity=quantity,
                        tab=tab,
                    )
                )

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
    ) -> None:
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
    ) -> None:
        self.event_manager.on(
            InventoryWeightEvent,
            callback=lambda _: self.on_ingredient_loaded(
                ingredient_info, ingredients_infos, max_possible_result_quantity
            ),
            originator=self,
            once=True,
        )
        self.logger.info(f"Current tab : {self.game_state.guild_chest.tab_number}")
        self.logger.info(f"Tab of item {ingredient_info.tab}")

        item = GuildChestState.get_item_by_gid(
            self.game_state.player.server_id,
            self.game_state.guild_chest.tab_number,
            ingredient_info.gid,
        )
        if item is None:
            self.logger.error(
                f"Item {ingredient_info.gid} not found in tab {self.game_state.guild_chest.tab_number}. Aborting recipe {self._current_recipe_being_loaded.resultId if self._current_recipe_being_loaded else 'unknown'}."
            )
            return self.abort_current_recipe()

        req = ExchangeObjectMoveRequest(
            object_uid=item.item.uid,
            quantity=-ingredient_info.quantity * max_possible_result_quantity,
        )
        self.send_message_delayed(req, SMALL_RANGE)

    def on_ingredient_loaded(
        self,
        ingredient_info: IngredientsInfo,
        ingredients_infos: list[IngredientsInfo],
        max_possible_result_quantity: int,
    ) -> None:
        total_quantity = ingredient_info.quantity * max_possible_result_quantity
        GuildChestState.release_reservation(
            self.game_state.player.server_id,
            ingredient_info.tab,
            ingredient_info.gid,
            total_quantity,
            self.game_state.player.character_name,
        )
        self.load_ingredient(ingredients_infos, max_possible_result_quantity)

    def abort_current_recipe(self) -> None:
        if self._current_recipe_being_loaded is None:
            return self.load_recipe()

        self.logger.warning(
            f"Aborting recipe {self._current_recipe_being_loaded.resultId} - missing ingredients"
        )

        server_id = self.game_state.player.server_id
        for ingredient_id, quantity in zip(
            self._current_recipe_being_loaded.ingredientIds,
            self._current_recipe_being_loaded.quantities,
        ):
            tab = GuildChestState.get_tab_for_gid(server_id, ingredient_id)
            if tab is not None:
                total_quantity = quantity * self._current_recipe_quantity
                GuildChestState.release_reservation(
                    server_id,
                    tab,
                    ingredient_id,
                    total_quantity,
                    self.game_state.player.character_name,
                )

        if self._current_recipe_being_loaded in self._remaining_recipes:
            self._remaining_recipes.remove(self._current_recipe_being_loaded)

        if self._current_recipe_being_loaded in [
            recipe for recipe, _ in self._loaded_recipes_infos
        ]:
            self._loaded_recipes_infos = [
                (recipe, qty)
                for recipe, qty in self._loaded_recipes_infos
                if recipe != self._current_recipe_being_loaded
            ]

        self._current_recipe_being_loaded = None
        self._current_recipe_quantity = 0

        self.load_recipe()

    def clear_behavior(self) -> None:
        GuildChestState.clear_all_reservations_for_bot(
            self.game_state.player.server_id,
            self.game_state.player.character_name,
        )
        super().clear_behavior()
