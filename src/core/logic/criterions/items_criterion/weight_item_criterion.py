from src.core.states.player_state import PlayerState
from src.core.logic.criterions.item_criterion import ItemCriterion


class WeightItemCriterion(ItemCriterion):

    def get_criterion(self, player_frame: PlayerState, *args, **kwargs) -> int:
        return player_frame.inventory_weight
