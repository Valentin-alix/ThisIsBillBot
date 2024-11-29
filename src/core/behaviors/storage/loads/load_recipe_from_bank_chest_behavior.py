from dataclasses import dataclass

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeObjectMoveRequest,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from dofus_unity_reader.models.datas.recipe_root import RecipeItem

from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.behaviors.storage.loads.recipe_loader_behavior import (
    RecipeLoaderBehavior,
)
from src.core.config import SMALL_RANGE


@dataclass
class LoadRecipeFromBankChestBehavior(RecipeLoaderBehavior):
    enter_bank_chest_behavior: EnterBankChestBehavior

    def enter_storage(self) -> None:
        self.enter_bank_chest_behavior.start(
            callback=self.on_entered_storage, parent=self
        )

    def on_entered_storage(self, error_code: str | None) -> None:
        if error_code is not None:
            return self.finish(
                error_code=error_code,
                loaded_recipes_infos=self._loaded_recipes_infos,
                remaining_recipes=self._remaining_recipes,
            )
        self.load_recipe()

    def get_storage_objects_by_gid(self) -> dict[int, ObjectItemInventory]:
        return self.game_state.inventory.bank_object_by_gid

    def load_ingredients_for_recipe(
        self, recipe: RecipeItem, max_possible_result_quantity: int
    ) -> None:
        ingredient_id_with_quantity = list(zip(recipe.ingredientIds, recipe.quantities))
        if len(ingredient_id_with_quantity) == 0:
            return self.load_recipe()
        self.load_ingredient(ingredient_id_with_quantity, max_possible_result_quantity)

    def load_ingredient(
        self,
        ingredient_id_with_quantity: list[tuple[int, int]],
        max_possible_result_quantity: int,
    ) -> None:
        if len(ingredient_id_with_quantity) == 0:
            return self.load_recipe()
        ingredient_id, quantity = ingredient_id_with_quantity.pop()
        self.event_manager.on(
            InventoryWeightEvent,
            callback=lambda _event: self.load_ingredient(
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
        self.send_message_delayed(req, SMALL_RANGE)
