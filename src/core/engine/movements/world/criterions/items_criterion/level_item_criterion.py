from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)


class LevelItemCriterion(ItemCriterion):
    def get_criterion(self, context: CriterionContext) -> int:
        return context.player_limited_level
