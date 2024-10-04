from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator


class GuildRightsItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        has_this_right = False
        socialFrame: SocialFrame = Kernel().worker.getFrameByName("SocialFrame")
        if not socialFrame.hasGuild:
            if self.item_operator.text == ItemCriterionOperator.DIFFERENT:
                return True
            return False
        guild: GuildWrapper = socialFrame.guild
        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_BOSS:
            has_this_right = guild.isBoss

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_BAN_MEMBERS:
            has_this_right = guild.banMembers

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_COLLECT:
            has_this_right = guild.collect

        if (
            self.criterion_value
            == GuildRightsBitEnum.GUILD_RIGHT_COLLECT_MY_TAX_COLLECTOR
        ):
            has_this_right = guild.collectMyTaxCollectors

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_DEFENSE_PRIORITY:
            has_this_right = guild.prioritizeMeInDefense

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_HIRE_TAX_COLLECTOR:
            has_this_right = guild.hireTaxCollector

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_INVITE_NEW_MEMBERS:
            has_this_right = guild.inviteNewMembers

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_MANAGE_GUILD_BOOSTS:
            has_this_right = guild.manageGuildBoosts

        if (
            self.criterion_value
            == GuildRightsBitEnum.GUILD_RIGHT_MANAGE_MY_XP_CONTRIBUTION
        ):
            has_this_right = guild.manageMyXpContribution

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_MANAGE_RANKS:
            has_this_right = guild.manageRanks

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_MANAGE_RIGHTS:
            has_this_right = guild.manageRights

        if (
            self.criterion_value
            == GuildRightsBitEnum.GUILD_RIGHT_MANAGE_XP_CONTRIBUTION
        ):
            has_this_right = guild.manageXPContribution

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_ORGANIZE_PADDOCKS:
            has_this_right = guild.organizeFarms

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_SET_ALLIANCE_PRISM:
            has_this_right = guild.setAlliancePrism

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_TALK_IN_ALLIANCE_CHAN:
            has_this_right = guild.talkInAllianceChannel

        if (
            self.criterion_value
            == GuildRightsBitEnum.GUILD_RIGHT_TAKE_OTHERS_MOUNTS_IN_PADDOCKS
        ):
            has_this_right = guild.takeOthersRidesInFarm

        if self.criterion_value == GuildRightsBitEnum.GUILD_RIGHT_USE_PADDOCKS:
            has_this_right = guild.useFarms

        if self.item_operator.text == ItemCriterionOperator.EQUAL:
            return has_this_right

        if self.item_operator.text == ItemCriterionOperator.DIFFERENT:
            return not has_this_right

        return False
