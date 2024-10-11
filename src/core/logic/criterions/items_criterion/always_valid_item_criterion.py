from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.game_state import GameState


class AlwaysValidItemCriterion(ItemCriterion):

    def is_respected(self, game_state: GameState) -> bool:
        return True
