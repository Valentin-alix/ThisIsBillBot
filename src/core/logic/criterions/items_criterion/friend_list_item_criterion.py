from src.core.logic.criterions.item_criterion import ItemCriterion


class FriendlistItemCriterion(ItemCriterion):
    def get_criterion(self, *args, **kwargs) -> int:
        return Kernel().worker.getFrameByName("SocialFrame")
