from src.core.logic.criterions.item_criterion import ItemCriterion


class GuildItemCriterion(ItemCriterion):
    def get_criterion(self, *args, **kwargs) -> int:
        guild: GuildWrapper = Kernel().worker.getFrameByName("SocialFrame")
        if guild:
            return 1
        return 0
