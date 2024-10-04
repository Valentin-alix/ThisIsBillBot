from src.core.logic.criterions.item_criterion import ItemCriterion


class PrestigeLevelItemCriterion(ItemCriterion):

    def get_criterion(self, *args, **kwargs) -> int:
        prestige = 0
        if PlayedCharacterManager().infos.level > ProtocolConstantsEnum.MAX_LEVEL:
            prestige = (
                PlayedCharacterManager().infos.level - ProtocolConstantsEnum.MAX_LEVEL
            )
        return prestige
