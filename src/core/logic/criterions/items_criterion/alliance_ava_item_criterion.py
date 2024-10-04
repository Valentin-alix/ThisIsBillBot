from src.core.logic.criterions.item_criterion import ItemCriterion


class AllianceAvAItemCriterion(ItemCriterion):
    def is_respected(self, *args, **kwargs) -> bool:
        aggressable: int = 0
        sub_area: SubArea = None
        current_prism: PrismSubAreaWrapper = None
        if self._operator.text == ItemCriterionOperator.EQUAL:
            aggressable = (
                PlayedCharacterManager().characteristics.alignmentInfos.aggressable
            )
            if (
                aggressable != AggressableStatusEnum.AvA_ENABLED_AGGRESSABLE
                and aggressable != AggressableStatusEnum.AvA_PREQUALIFIED_AGGRESSABLE
            ):
                return False
            sub_area = PlayedCharacterManager().currentSubArea
            current_prism = AllianceFrame().getPrismSubAreaById(sub_area.id)
            if not current_prism or current_prism.mapId == -1:
                return False
            if current_prism.state != PrismStateEnum.PRISM_STATE_VULNERABLE:
                return False
            return True
        return False
