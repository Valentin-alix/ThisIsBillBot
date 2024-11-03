from dataclasses import dataclass, field
from enum import StrEnum, auto

from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMoveRequest,
)
from d3_mapping.resources.protos.game.inventory_pb2 import InventoryWeightEvent
from data_center.i18n import I18N
from models.datas.recipe_root import RecipeItem

from src.core.behaviors.behavior import Behavior
from src.core.config.storage import USEFUL_UNLOAD
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config.timings import BASE_RANGE, SMALL_RANGE
from src.core.logic.craft.craft import (
    get_max_possible_result_quantity,
    get_max_result_quantity,
)


class LoadFromBankError(StrEnum):
    NOT_ENOUGH_LVL = auto()
    NOT_ENOUGH_KAMAS = auto()


@dataclass
class LoadRecipeFromBankChestBehavior(Behavior):
    enter_bank_chest_behavior: EnterBankChestBehavior
    unload_behavior: UnloadBehavior

    _remaining_recipes: list[RecipeItem] = field(init=False, default_factory=list)
    _loaded_recipes_infos: list[tuple[RecipeItem, int]] = field(
        init=False, default_factory=list
    )

    def run(self, recipes: list[RecipeItem]) -> None:
        # le machin se fait par recette ? et pas d'un coup ?
        self._remaining_recipes = recipes.copy()
        self._loaded_recipes_infos = []

        if self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:
            return self.unload_behavior.start(
                callback=self.on_unload_behavior_finished, parent=self
            )
        self.on_unloaded()

    def on_unload_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            return self.finish(
                error_code=error_code,
                loaded_recipes_infos=self._loaded_recipes_infos,
                remaining_recipes=self._remaining_recipes,
            )
        self.on_unloaded()

    def on_unloaded(self):
        self.run_timer(
            BASE_RANGE,
            lambda: self.enter_bank_chest_behavior.start(
                callback=self.on_entered_bank_chest_behavior, parent=self
            ),
        )

    def on_entered_bank_chest_behavior(self, error_code: str | None):
        if error_code is not None:
            return self.finish(
                error_code=error_code,
                loaded_recipes_infos=self._loaded_recipes_infos,
                remaining_recipes=self._remaining_recipes,
            )
        self.load_item()

    def load_item(self):
        if len(self._remaining_recipes) == 0:
            return self.on_full_loaded()

        recipe = self._remaining_recipes[0]
        self.logger.info(
            f"bank object by gid on load item: {list(self.game_state.inventory.bank_object_by_gid.keys())}"
        )
        max_result_quantity, weight_for_one_result = get_max_result_quantity(
            self.logger, self.game_state.inventory.bank_object_by_gid, recipe
        )
        if max_result_quantity == 0:
            # we have no more enough ingredient in bank chest for this recipe
            self._remaining_recipes.remove(recipe)
            return self.load_item()

        ingredient_id_with_quantity = list(zip(recipe.ingredientIds, recipe.quantities))

        if len(ingredient_id_with_quantity) == 0:
            return self.on_full_loaded()

        self.logger.info(
            f"We can craft {max_result_quantity} of recipe {I18N().name_by_id[int(recipe.resultNameId)]} so lezz go"
        )

        max_possible_result_quantity = get_max_possible_result_quantity(
            self.game_state.inventory.weight_max,
            self.game_state.inventory.inventory_weight,
            weight_for_one_result,
            max_result_quantity,
        )
        if max_possible_result_quantity == 0:
            # player need more free weight
            return self.on_full_loaded()

        self.logger.info(
            f"We can craft in inventory {max_possible_result_quantity} of recipe {I18N().name_by_id[int(recipe.resultNameId)]} so lezz go"
        )
        self._loaded_recipes_infos.append((recipe, max_possible_result_quantity))
        self.load_ingredient(ingredient_id_with_quantity, max_possible_result_quantity)

    def load_ingredient(
        self,
        ingredient_id_with_quantity: list[tuple[int, int]],
        max_possible_result_quantity: int,
    ):
        if len(ingredient_id_with_quantity) == 0:
            return self.load_item()
        ingredient_id, quantity = ingredient_id_with_quantity.pop()
        self.event_manager.on(
            InventoryWeightEvent,
            callback=lambda _: self.load_ingredient(
                ingredient_id_with_quantity, max_possible_result_quantity
            ),
            originator=self,
            once=True,
        )
        req = ExchangeObjectMoveRequest(
            object_uid=self.game_state.inventory.bank_object_by_gid[
                ingredient_id
            ].item.uid,
            quantity=-quantity * max_possible_result_quantity,
        )
        self.run_timer(SMALL_RANGE, lambda: self.event_manager.send(req))

    def on_full_loaded(self):
        self.event_manager.on(
            ExchangeLeaveEvent,
            callback=lambda _: self.finish(
                loaded_recipes_infos=self._loaded_recipes_infos,
                remaining_recipes=self._remaining_recipes,
            ),
            originator=self,
            once=True,
        )
        self.run_timer(BASE_RANGE, self.leave_all_dialogs)

    def leave_all_dialogs(self):
        request = DialogLeaveRequest()
        self.event_manager.send(request)
