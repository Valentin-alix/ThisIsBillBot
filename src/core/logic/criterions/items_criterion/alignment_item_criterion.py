from src.core.logic.criterions.item_criterion import ItemCriterion


class AlignmentItemCriterion(ItemCriterion):

    def get_criterion(self, *args, **kwargs) -> int:
        return PlayedCharacterManager().characteristics.alignmentInfos.alignmentSide
