from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator


class CommunityItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        serverCommunity: int = PlayerManager().server.communityId
        if self.item_operator.text == ItemCriterionOperator.EQUAL:
            return serverCommunity == self.criterion_value
        elif self.item_operator.text == ItemCriterionOperator.DIFFERENT:
            return serverCommunity != self.criterion_value
        else:
            return False
