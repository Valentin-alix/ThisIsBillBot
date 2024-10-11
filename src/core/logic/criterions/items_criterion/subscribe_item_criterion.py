from datetime import datetime

from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.game_state import GameState


class SubscribeItemCriterion(ItemCriterion):

    def get_criterion(self, game_state: GameState) -> int:
        if (
            datetime.now(game_state.player.subscription_end_date.tzinfo)
            < game_state.player.subscription_end_date
        ):
            return 1
        return 0
