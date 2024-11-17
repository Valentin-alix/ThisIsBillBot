from abc import abstractmethod
from dataclasses import dataclass, field

from D3Database.data_center.i18n import I18N
from D3Database.models.datas.recipe_root import RecipeItem
from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import ExchangeLeaveEvent
from src.core.behaviors.dialog_handler_behavior import DialogHandlerBehavior
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config import BASE_RANGE, USEFUL_UNLOAD
from src.core.engine.crafts.recipes import (
    get_max_possible_result_quantity,
    get_max_result_quantity,
)


@dataclass
class RecipeLoaderBehavior(DialogHandlerBehavior):
    unload_behavior: UnloadBehavior

    _remaining_recipes: list[RecipeItem] = field(init=False, default_factory=list)
    _loaded_recipes_infos: list[tuple[RecipeItem, int]] = field(
        init=False, default_factory=list
    )

    @abstractmethod
    def enter_storage(self) -> None:
        pass

    @abstractmethod
    def get_storage_objects_by_gid(self) -> dict:
        pass

    @abstractmethod
    def load_ingredients_for_recipe(
        self, recipe: RecipeItem, max_possible_result_quantity: int
    ) -> None:
        pass

    def run(self, recipes: list[RecipeItem]) -> None:
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
        self.run_timer(BASE_RANGE, self.enter_storage)

    def load_recipe(self):
        if len(self._remaining_recipes) == 0:
            return self.on_full_loaded()

        recipe = self._remaining_recipes[0]
        objects_by_gid = self.get_storage_objects_by_gid()
        max_result_quantity, weight_for_one_result = get_max_result_quantity(
            self.logger, objects_by_gid, recipe
        )
        if max_result_quantity == 0:
            self._remaining_recipes.remove(recipe)
            return self.load_recipe()

        self.logger.info(
            f"We can craft {max_result_quantity} of recipe {I18N().name_by_id[int(recipe.resultNameId)]}"
        )
        max_possible_result_quantity = get_max_possible_result_quantity(
            self.game_state.inventory.weight_max,
            self.game_state.inventory.inventory_weight,
            weight_for_one_result,
            max_result_quantity,
        )
        if max_possible_result_quantity == 0:
            return self.on_full_loaded()

        self.logger.info(
            f"We can craft in inventory {max_possible_result_quantity} of recipe {I18N().name_by_id[int(recipe.resultNameId)]}"
        )
        self._loaded_recipes_infos.append((recipe, max_possible_result_quantity))
        self.reserve_ingredients_for_recipe(recipe, max_possible_result_quantity)
        self.load_ingredients_for_recipe(recipe, max_possible_result_quantity)

    def reserve_ingredients_for_recipe(
        self, recipe: RecipeItem, max_possible_result_quantity: int
    ) -> None:
        pass

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
        self.leave_dialog()
