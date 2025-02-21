from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)
from src.core.engine.movements.world.criterions.item_criterion_operator import (
    ItemCriterionOperator,
)


class SubareaItemCriterion(ItemCriterion):
    def is_respected(self, context: CriterionContext) -> bool:
        if self.item_operator.text in [
            ItemCriterionOperator.EQUAL,
            ItemCriterionOperator.DIFFERENT,
        ]:
            return super().is_respected(context)
        else:
            return False

    def get_criterion(self, context: CriterionContext) -> int:
        return context.sub_area_id
