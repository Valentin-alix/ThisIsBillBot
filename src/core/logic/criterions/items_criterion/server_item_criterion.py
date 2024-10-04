from src.core.logic.criterions.item_criterion import ItemCriterion


class ServerItemCriterion(ItemCriterion):

    def get_criterion(self, *args, **kwargs) -> int:
        return PlayerManager().server.id
