from dataclasses import dataclass
from functools import partial

from models.datas.recipe_root import RecipeItem
from protos.game.dialog_pb2 import DialogLeaveRequest
from protos.game.exchange_pb2 import ExchangeObjectMoveRequest, ExchangeLeaveEvent
from protos.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
    GuildChestTabSelectRequest,
)
from protos.game.inventory_pb2 import InventoryWeightEvent
from src.const import BASE_RANGE, SMALL_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.storage.consts import USEFUL_UNLOAD, GUILD_CONTENT_BY_TAB
from src.core.behaviors.storage.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.behaviors.storage.unload_behavior import UnloadBehavior
from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB
from src.exceptions import UnhandledErrorCodeException


@dataclass
class LoadRecipeFromGuildChestBehavior(Behavior):
    enter_guild_chest_behavior: EnterGuildChestBehavior
    unload_behavior: UnloadBehavior

    def run(self, recipe: RecipeItem) -> None:
        if not self.is_creatable_recipe(recipe):
            self.logger.warning("recipe is not creatable.")
            return self.finish(max_possible_result_quantity=0)
        if self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:
            return self.unload_behavior.start(
                callback=partial(self.on_unload_behavior_finished, recipe=recipe),
                parent=self,
            )
        self.on_unloaded(recipe)

    def is_creatable_recipe(self, recipe: RecipeItem) -> bool:
        return all(
            ingredient_id
            in [
                item_gid
                for content_gids in GUILD_CONTENT_BY_TAB.values()
                for item_gid in content_gids
            ]
            for ingredient_id in recipe.ingredientIds
        )

    def on_unload_behavior_finished(self, error_code: str | None, recipe: RecipeItem):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.on_unloaded(recipe)

    def on_unloaded(self, recipe: RecipeItem):
        self.run_timer(
            BASE_RANGE,
            lambda: self.enter_guild_chest_behavior.start(
                callback=partial(self.on_entered_guild_chest_behavior, recipe=recipe),
                parent=self,
            ),
        )

    def on_entered_guild_chest_behavior(
        self, error_code: str | None, recipe: RecipeItem
    ):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        tab_to_discovers = {
            tab
            for tab, item_gids in GUILD_CONTENT_BY_TAB.items()
            if any(
                ingredient_id in item_gids and tab not in CHEST_OBJECT_BY_GID_BY_TAB
                for ingredient_id in recipe.ingredientIds
            )
        }
        self.discover_tabs(tab_to_discovers, recipe)

    def discover_tabs(self, tabs: set[int], recipe: RecipeItem):
        if len(tabs) == 0:
            return self.on_discovered_tabs(recipe)

        self.event_manager.on(
            GuildChestCurrentListenersAddEvent,
            partial(
                self.on_guild_chest_current_listeners_add_event_after_changed_tab,
                tabs=tabs,
                recipe=recipe,
            ),
            once=True,
            originator=self,
        )
        tab = tabs.pop()
        self.logger.info(f"Gonna discover tab {tab}")
        return self.run_timer(
            SMALL_RANGE,
            lambda: self.event_manager.send(GuildChestTabSelectRequest(tab_number=tab)),
        )

    def on_guild_chest_current_listeners_add_event_after_changed_tab(
        self,
        msg: GuildChestCurrentListenersAddEvent,
        tabs: set[int],
        recipe: RecipeItem,
    ):
        self.discover_tabs(tabs, recipe)

    def on_discovered_tabs(self, recipe: RecipeItem):
        max_possible_result_quantity = self.get_max_possible_result_quantity(recipe)
        if max_possible_result_quantity == 0:
            return self.on_full_loaded(max_possible_result_quantity=0)

        ingredient_id_with_quantity_and_tab = [
            (
                ingredient_id,
                next(
                    tab
                    for tab, item_gids in CHEST_OBJECT_BY_GID_BY_TAB.items()
                    if ingredient_id in item_gids
                ),
                quantity,
            )
            for ingredient_id, quantity in zip(recipe.ingredientIds, recipe.quantities)
        ]
        ingredient_id_with_quantity_and_tab.sort(
            key=lambda elem: (
                elem[1] == self.game_state.guild_chest.tab_number,
                elem[1],
            )
        )
        self.load_item(
            ingredient_id_with_quantity_and_tab=ingredient_id_with_quantity_and_tab,
            max_possible_result_quantity=max_possible_result_quantity,
        )

    def load_item(
        self,
        ingredient_id_with_quantity_and_tab: list[tuple[int, int, int]],
        max_possible_result_quantity: int,
    ):
        if len(ingredient_id_with_quantity_and_tab) == 0:
            return self.on_full_loaded(
                max_possible_result_quantity=max_possible_result_quantity
            )
        ingredient_id, tab, quantity = ingredient_id_with_quantity_and_tab.pop()
        if self.game_state.guild_chest.tab_number != tab:
            self.event_manager.on(
                GuildChestCurrentListenersAddEvent,
                lambda _: self.on_tab_of_item_to_load(
                    ingredient_id,
                    quantity,
                    ingredient_id_with_quantity_and_tab,
                    max_possible_result_quantity,
                ),
                once=True,
                originator=self,
            )
            return self.run_timer(
                SMALL_RANGE,
                lambda: self.event_manager.send(
                    GuildChestTabSelectRequest(tab_number=tab)
                ),
            )
        self.on_tab_of_item_to_load(
            ingredient_id,
            quantity,
            ingredient_id_with_quantity_and_tab,
            max_possible_result_quantity,
        )

    def on_tab_of_item_to_load(
        self,
        ingredient_id: int,
        quantity: int,
        ingredient_id_with_quantity_and_tab: list[tuple[int, int, int]],
        max_possible_result_quantity: int,
    ):
        self.event_manager.on(
            InventoryWeightEvent,
            callback=lambda _: self.on_item_loaded(
                ingredient_id_with_quantity_and_tab, max_possible_result_quantity
            ),
            originator=self,
            once=True,
        )
        self.logger.info(f"Current tab : {self.game_state.guild_chest.tab_number}")
        req = ExchangeObjectMoveRequest(
            object_uid=CHEST_OBJECT_BY_GID_BY_TAB[
                self.game_state.guild_chest.tab_number
            ][ingredient_id].item.uid,
            quantity=-quantity * max_possible_result_quantity,
        )
        self.run_timer(SMALL_RANGE, lambda: self.event_manager.send(req))

    def on_full_loaded(self, max_possible_result_quantity: int):
        self.event_manager.on(
            ExchangeLeaveEvent,
            callback=lambda _: self.finish(
                max_possible_result_quantity=max_possible_result_quantity
            ),
            originator=self,
            once=True,
        )
        self.leave_all_dialogs()

    def on_item_loaded(
        self,
        ingredient_id_with_quantity_and_tab: list[tuple[int, int, int]],
        max_possible_result_quantity: int,
    ):
        self.load_item(
            ingredient_id_with_quantity_and_tab, max_possible_result_quantity
        )

    def get_max_possible_result_quantity(self, recipe: RecipeItem) -> int:
        min_result_quantity: int | None = None
        weight_for_one_result = 0

        for ingredient_id, quantity in zip(recipe.ingredientIds, recipe.quantities):
            ingredient_in_chest = next(
                (
                    related_item
                    for content in CHEST_OBJECT_BY_GID_BY_TAB.values()
                    if (related_item := content.get(ingredient_id)) is not None
                ),
                None,
            )
            if ingredient_in_chest is None:
                self.logger.info(
                    f"ingredient {I18N.name_by_id[DataReader().item_by_id[ingredient_id].nameId]} not in chest, can't "
                    f"craft recipe"
                )
                return 0
            if ingredient_in_chest.item.quantity < quantity:
                self.logger.info(
                    f"ingredient {I18N.name_by_id[DataReader().item_by_id[ingredient_id].nameId]} don't have enough "
                    f"quantity, can't craft recipe"
                )
                return 0
            result_quantity = ingredient_in_chest.item.quantity // quantity
            if min_result_quantity is None or result_quantity < min_result_quantity:
                min_result_quantity = result_quantity
            weight_for_one_result += (
                quantity * DataReader().item_by_id[ingredient_id].realWeight
            )

        player_weight = (
            self.game_state.inventory.weight_max
            - self.game_state.inventory.inventory_weight
        )
        max_possible_result_quantity = min(
            player_weight // weight_for_one_result, min_result_quantity
        )
        return max_possible_result_quantity

    def leave_all_dialogs(self):
        request = DialogLeaveRequest()
        self.event_manager.send(request)
        self.event_manager.send(request)
