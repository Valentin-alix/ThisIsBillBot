from src.core.states.player_state import PlayerState
from src.core.logic.criterions.item_criterion import ItemCriterion


class SubscriptionDurationItemCriterion(ItemCriterion):
    def get_criterion(self, player_frame: PlayerState, *args, **kwargs) -> int:
        return math.floor(PlayerManager().subscriptionDurationElapsed / (24 * 60 * 60))
