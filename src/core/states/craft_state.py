from dataclasses import dataclass

from D3Database.models.datas.recipe_root import RecipeItem
from src.core.engine.crafts.recipes import get_valid_recipes
from src.core.states.player_state import PlayerState
from src.core.states.state import State


@dataclass
class CraftState(State):
    player_state: PlayerState

    def get_valid_recipes(
        self,
        recipes: list[RecipeItem],
    ) -> list[RecipeItem]:
        return get_valid_recipes(self.logger, self.player_state.jobs_lvl_by_id, recipes)
