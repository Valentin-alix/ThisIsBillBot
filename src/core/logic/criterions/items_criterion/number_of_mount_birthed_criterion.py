from src.core.states.player_state import PlayerState
from src.core.logic.criterions.item_criterion import ItemCriterion


class NumberOfMountBirthedCriterion(ItemCriterion):
    def get_criterion(self, player_state: PlayerState, *args, **kwargs) -> int:
        return 0
