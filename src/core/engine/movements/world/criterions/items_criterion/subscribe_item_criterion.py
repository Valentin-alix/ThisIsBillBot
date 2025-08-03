from datetime import datetime

from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)


class SubscribeItemCriterion(ItemCriterion):
    def get_criterion(self, context: CriterionContext) -> int:
        if datetime.now(context.player_subscription_end_date.tzinfo) < context.player_subscription_end_date:
            return 1
        return 0
