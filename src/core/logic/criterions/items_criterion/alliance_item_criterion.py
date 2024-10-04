from src.core.logic.criterions.item_criterion import ItemCriterion


class AllianceItemCriterion(ItemCriterion):
    def get_criterion(self, *args, **kwargs) -> int:
        alliance: AllianceWrapper = AllianceFrame().alliance
        if alliance:
            return 1
        return 0
