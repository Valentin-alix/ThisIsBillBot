from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)


class StaticCriterionItemCriterion(ItemCriterion):
    def is_respected(self, context: CriterionContext) -> bool:
        return True
