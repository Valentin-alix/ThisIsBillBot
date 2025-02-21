import datetime

from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)


class MonthItemCriterion(ItemCriterion):
    def get_criterion(self, context: CriterionContext) -> int:
        return datetime.datetime.now().month - 1
