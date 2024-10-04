from src.core.logic.criterions.item_criterion import ItemCriterion


class PremiumAccountItemCriterion(ItemCriterion):
    def get_criterion(self, *args, **kwargs) -> int:
        return 0
