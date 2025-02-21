from dofus_unity_reader.data_center.data_reader import DataReader

from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)
from src.core.engine.movements.world.criterions.item_criterion_operator import (
    ItemCriterionOperator,
)


class AreaItemCriterion(ItemCriterion):
    def is_respected(self, context: CriterionContext) -> bool:
        if (
            self.item_operator.text == ItemCriterionOperator.EQUAL
            or self.item_operator.text == ItemCriterionOperator.DIFFERENT
        ):
            return super().is_respected(context)
        else:
            return False

    def get_criterion(self, context: CriterionContext) -> int:
        return DataReader().sub_area_by_id[context.sub_area_id].areaId
