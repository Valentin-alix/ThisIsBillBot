from src.core.logic.criterions.item_criterion import ItemCriterion


class SpecializationItemCriterion(ItemCriterion):

    def get_criterion(self, *args, **kwargs) -> int:
        return Kernel().alignmentFrame.playerRank
