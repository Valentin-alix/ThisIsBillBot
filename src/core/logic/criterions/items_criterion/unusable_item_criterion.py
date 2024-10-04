from src.core.states.player_state import PlayerState
from src.core.logic.criterions.item_criterion import ItemCriterion


class UnusableItemCriterion(ItemCriterion):
    def is_respected(self, player_state: PlayerState, *args, **kwargs) -> bool:
        return True
