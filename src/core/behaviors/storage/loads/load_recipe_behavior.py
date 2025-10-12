from dataclasses import dataclass

from DBDofusUnity.dofus_unity_reader.models.datas.recipe_root import RecipeItem

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.storage.loads.load_recipe_from_bank_chest_behavior import (
    LoadRecipeFromBankChestBehavior,
)
from src.core.behaviors.storage.loads.load_recipe_from_guild_chest_behavior import (
    LoadRecipeFromGuildChestBehavior,
)


@dataclass
class LoadRecipeBehavior(Behavior):
    load_recipe_from_bank_chest_behavior: LoadRecipeFromBankChestBehavior
    load_recipe_from_guild_chest_behavior: LoadRecipeFromGuildChestBehavior

    def run(self, recipes: list[RecipeItem]) -> None:
        if self.game_state.player.is_sub and self.game_state.guild_chest.can_access_guild_chest:
            self.load_recipe_from_guild_chest_behavior.start(
                callback=self.on_load_from_chest_behavior_finished,
                parent=self,
                recipes=recipes,
            )
        else:
            self.load_recipe_from_bank_chest_behavior.start(
                callback=self.on_load_from_chest_behavior_finished,
                parent=self,
                recipes=recipes,
            )

    def on_load_from_chest_behavior_finished(
        self,
        error_code: str | None,
        loaded_recipes_infos: list[tuple[RecipeItem, int]],
        remaining_recipes: list[RecipeItem],
    ):
        self.raise_if_error(error_code)
        self.finish(
            loaded_recipes_infos=loaded_recipes_infos,
            remaining_recipes=remaining_recipes,
        )
