from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator


class AreaItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        if (
            self.item_operator.text == ItemCriterionOperator.EQUAL
            or self.item_operator.text == ItemCriterionOperator.DIFFERENT
        ):
            return super().is_respected()
        else:
            return False

    def get_criterion(self, *args, **kwargs) -> int:
        return PlayedCharacterManager().currentSubArea.area.id
