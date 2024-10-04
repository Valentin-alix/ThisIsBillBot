from src.core.logic.criterions.item_criterion import ItemCriterion


class GuildLevelItemCriterion(ItemCriterion):

    def get_criterion(self, *args, **kwargs) -> int:
        guild: GuildWrapper = Kernel().worker.getFrameByName("SocialFrame")
        if guild:
            return guild.level
        return 0
