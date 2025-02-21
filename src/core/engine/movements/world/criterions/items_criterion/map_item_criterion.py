from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)


class MapItemCriterion(ItemCriterion):
    def get_criterion(self, context: CriterionContext) -> int:
        return context.map_id
