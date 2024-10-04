from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator


class AllianceRightsItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        has_this_right: bool = False
        if not AllianceFrame().hasAlliance:
            if self.operator.text == ItemCriterionOperator.DIFFERENT:
                return True
            return False
        alliance: AllianceWrapper = AllianceFrame().alliance
        if self.value == AllianceRightsBitEnum.ALLIANCE_RIGHT_BOSS:
            has_this_right = alliance.isBoss
        else:
            has_this_right = True
        if self.operator.text == ItemCriterionOperator.EQUAL:
            return has_this_right
        if self.operator.text == ItemCriterionOperator.DIFFERENT:
            return not has_this_right
        else:
            return False
