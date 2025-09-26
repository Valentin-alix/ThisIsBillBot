from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)
from src.core.engine.movements.world.criterions.item_criterion_operator import (
    ItemCriterionOperator,
)


class StateCriterion(ItemCriterion):
    def is_respected(self, context: CriterionContext) -> bool:
        match self.item_operator.text:
            case ItemCriterionOperator.EQUAL:
                ...
            case ItemCriterionOperator.DIFFERENT:
                ...
            case _:
                return False
        return False
