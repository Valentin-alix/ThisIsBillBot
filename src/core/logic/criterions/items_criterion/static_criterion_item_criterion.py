from src.core.logic.criterions.item_criterion import ItemCriterion


class StaticCriterionItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        return True

    def get_criterion(self, *args, **kwargs) -> int:
        return 0
