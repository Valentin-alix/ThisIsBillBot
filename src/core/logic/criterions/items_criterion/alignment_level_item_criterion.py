from src.core.logic.criterions.item_criterion import ItemCriterion


class AlignmentLevelItemCriterion(ItemCriterion):
    def get_criterion(self, *args, **kwargs) -> int:
        alignInfo: ActorExtendedAlignmentInformations = (
            PlayedCharacterManager().characteristics.alignmentInfos
        )
        return alignInfo.alignmentValue
