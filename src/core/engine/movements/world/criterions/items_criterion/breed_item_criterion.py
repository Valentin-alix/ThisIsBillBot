from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)
from src.core.states.game_state import GameState


class BreedItemCriterion(ItemCriterion):
    def get_criterion(self, game_state: GameState) -> int:
        return game_state.fight.breed_id
