from src.core.logic.criterions.item_criterion import ItemCriterion


class SubscribeItemCriterion(ItemCriterion):

    def get_criterion(self, *args, **kwargs) -> int:
        time_remaining: float = PlayerManager().subscriptionEndDate
        if time_remaining > 0 or PlayerManager().hasRights:
            return 1
        return 0
