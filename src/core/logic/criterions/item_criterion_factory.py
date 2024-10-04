from src.core.logic.criterions.interface_item_criterion import IItemCriterion
from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.items_criterion.account_rights_item_criterion import (
    AccountRightsItemCriterion,
)
from src.core.logic.criterions.items_criterion.achievement_account_item_criterion import (
    AchievementAccountItemCriterion,
)
from src.core.logic.criterions.items_criterion.achievement_item_criterion import (
    AchievementItemCriterion,
)
from src.core.logic.criterions.items_criterion.achievement_objective_validated import (
    AchievementObjectiveValidated,
)
from src.core.logic.criterions.items_criterion.achievement_points_item_criterion import (
    AchievementPointsItemCriterion,
)
from src.core.logic.criterions.items_criterion.alignment_item_criterion import (
    AlignmentItemCriterion,
)
from src.core.logic.criterions.items_criterion.alignment_level_item_criterion import (
    AlignmentLevelItemCriterion,
)
from src.core.logic.criterions.items_criterion.alliance_ava_item_criterion import (
    AllianceAvAItemCriterion,
)
from src.core.logic.criterions.items_criterion.alliance_item_criterion import (
    AllianceItemCriterion,
)
from src.core.logic.criterions.items_criterion.alliance_rights_item_criterion import (
    AllianceRightsItemCriterion,
)
from src.core.logic.criterions.items_criterion.area_item_criterion import (
    AreaItemCriterion,
)
from src.core.logic.criterions.items_criterion.arena_duel_rank_criterion import (
    ArenaDuelRankCriterion,
)
from src.core.logic.criterions.items_criterion.arena_max_duel_rank_criterion import (
    ArenaMaxDuelRankCriterion,
)
from src.core.logic.criterions.items_criterion.arena_max_solo_rank_criterion import (
    ArenaMaxSoloRankCriterion,
)
from src.core.logic.criterions.items_criterion.arena_max_team_rank_criterion import (
    ArenaMaxTeamRankCriterion,
)
from src.core.logic.criterions.items_criterion.arena_solo_rank_criterion import (
    ArenaSoloRankCriterion,
)
from src.core.logic.criterions.items_criterion.arena_team_rank_criterion import (
    ArenaTeamRankCriterion,
)
from src.core.logic.criterions.items_criterion.bones_item_criterion import (
    BonesItemCriterion,
)
from src.core.logic.criterions.items_criterion.bonus_set_item_criterion import (
    BonusSetItemCriterion,
)
from src.core.logic.criterions.items_criterion.breed_item_criterion import (
    BreedItemCriterion,
)
from src.core.logic.criterions.items_criterion.community_item_criterion import (
    CommunityItemCriterion,
)
from src.core.logic.criterions.items_criterion.day_item_criterion import (
    DayItemCriterion,
)
from src.core.logic.criterions.items_criterion.emote_item_criterion import (
    EmoteItemCriterion,
)
from src.core.logic.criterions.items_criterion.friend_list_item_criterion import (
    FriendlistItemCriterion,
)
from src.core.logic.criterions.items_criterion.gift_item_criterion import (
    GiftItemCriterion,
)
from src.core.logic.criterions.items_criterion.guild_item_criterion import (
    GuildItemCriterion,
)
from src.core.logic.criterions.items_criterion.guild_level_item_criterion import (
    GuildLevelItemCriterion,
)
from src.core.logic.criterions.items_criterion.guild_rights_item_criterion import (
    GuildRightsItemCriterion,
)
from src.core.logic.criterions.items_criterion.job_item_criterion import (
    JobItemCriterion,
)
from src.core.logic.criterions.items_criterion.kama_item_criterion import (
    KamaItemCriterion,
)
from src.core.logic.criterions.items_criterion.level_item_criterion import (
    LevelItemCriterion,
)
from src.core.logic.criterions.items_criterion.map_characters_item_criterion import (
    MapCharactersItemCriterion,
)
from src.core.logic.criterions.items_criterion.map_item_criterion import (
    MapItemCriterion,
)
from src.core.logic.criterions.items_criterion.maried_item_criterion import (
    MariedItemCriterion,
)
from src.core.logic.criterions.items_criterion.monster_group_challenge_criterion import (
    MonsterGroupChallengeCriterion,
)
from src.core.logic.criterions.items_criterion.month_item_criterion import (
    MonthItemCriterion,
)
from src.core.logic.criterions.items_criterion.mount_family_item_criterion import (
    MountFamilyItemCriterion,
)
from src.core.logic.criterions.items_criterion.name_item_criterion import (
    NameItemCriterion,
)
from src.core.logic.criterions.items_criterion.new_haven_bag_item_criterion import (
    NewHavenbagItemCriterion,
)
from src.core.logic.criterions.items_criterion.number_of_item_made_criterion import (
    NumberOfItemMadeCriterion,
)
from src.core.logic.criterions.items_criterion.number_of_mount_birthed_criterion import (
    NumberOfMountBirthedCriterion,
)
from src.core.logic.criterions.items_criterion.object_item_criterion import (
    ObjectItemCriterion,
)
from src.core.logic.criterions.items_criterion.premium_account_item_criterion import (
    PremiumAccountItemCriterion,
)
from src.core.logic.criterions.items_criterion.prestive_level_item_criterion import (
    PrestigeLevelItemCriterion,
)
from src.core.logic.criterions.items_criterion.pvp_rank_item_criterion import (
    PVPRankItemCriterion,
)
from src.core.logic.criterions.items_criterion.quest_item_criterion import (
    QuestItemCriterion,
)
from src.core.logic.criterions.items_criterion.quest_objective_item_criterion import (
    QuestObjectiveItemCriterion,
)
from src.core.logic.criterions.items_criterion.ride_item_criterion import (
    RideItemCriterion,
)
from src.core.logic.criterions.items_criterion.rune_by_breaking_item_criterion import (
    RuneByBreakingItemCriterion,
)
from src.core.logic.criterions.items_criterion.server_item_criterion import (
    ServerItemCriterion,
)
from src.core.logic.criterions.items_criterion.server_season_temporis_criterion import (
    ServerSeasonTemporisCriterion,
)
from src.core.logic.criterions.items_criterion.server_type_item_criterion import (
    ServerTypeItemCriterion,
)
from src.core.logic.criterions.items_criterion.sex_item_criterion import (
    SexItemCriterion,
)
from src.core.logic.criterions.items_criterion.skill_item_criterion import (
    SkillItemCriterion,
)
from src.core.logic.criterions.items_criterion.smiley_pack_item_criterion import (
    SmileyPackItemCriterion,
)
from src.core.logic.criterions.items_criterion.soul_stone_item_criterion import (
    SoulStoneItemCriterion,
)
from src.core.logic.criterions.items_criterion.specialization_item_criterion import (
    SpecializationItemCriterion,
)
from src.core.logic.criterions.items_criterion.spell_item_criterion import (
    SpellItemCriterion,
)
from src.core.logic.criterions.items_criterion.static_criterion_item_criterion import (
    StaticCriterionItemCriterion,
)
from src.core.logic.criterions.items_criterion.sub_area_item_criterion import (
    SubareaItemCriterion,
)
from src.core.logic.criterions.items_criterion.subscribe_item_criterion import (
    SubscribeItemCriterion,
)
from src.core.logic.criterions.items_criterion.subscription_duration_item_criterion import (
    SubscriptionDurationItemCriterion,
)
from src.core.logic.criterions.items_criterion.unusable_item_criterion import (
    UnusableItemCriterion,
)
from src.core.logic.criterions.items_criterion.weight_item_criterion import (
    WeightItemCriterion,
)


class ItemCriterionFactory:
    @staticmethod
    def create(criterion: str) -> IItemCriterion | None:
        type_criterion = criterion[0:2]

        item_criterion: IItemCriterion

        if type_criterion == "BI":
            item_criterion = UnusableItemCriterion(criterion)
        elif type_criterion in [
            "Ca",
            "CA",
            "ca",
            "Cc",
            "CC",
            "cc",
            "CD",
            "Ce",
            "CE",
            "CH",
            "Ci",
            "CI",
            "ci",
            "CL",
            "CM",
            "CP",
            "Cs",
            "CS",
            "cs",
            "Ct",
            "CT",
            "Cv",
            "CV",
            "cv",
            "Cw",
            "CW",
            "cw",
        ]:
            item_criterion = ItemCriterion(criterion)
        elif type_criterion == "EA":
            item_criterion = MonsterGroupChallengeCriterion(criterion)
        elif type_criterion == "EB":
            item_criterion = NumberOfMountBirthedCriterion(criterion)
        elif type_criterion == "Ec":
            item_criterion = NumberOfItemMadeCriterion(criterion)
        elif type_criterion == "Eu":
            item_criterion = RuneByBreakingItemCriterion(criterion)
        elif type_criterion == "Kd":
            item_criterion = ArenaDuelRankCriterion(criterion)  # TODO
        elif type_criterion == "KD":
            item_criterion = ArenaMaxDuelRankCriterion(criterion)  # TODO
        elif type_criterion == "Ks":
            item_criterion = ArenaSoloRankCriterion(criterion)  # TODO
        elif type_criterion == "KS":
            item_criterion = ArenaMaxSoloRankCriterion(criterion)  # TODO
        elif type_criterion == "Kt":
            item_criterion = ArenaTeamRankCriterion(criterion)  # TODO
        elif type_criterion == "KT":
            item_criterion = ArenaMaxTeamRankCriterion(criterion)  # TODO
        elif type_criterion == "MK":
            item_criterion = MapCharactersItemCriterion(criterion)
        elif type_criterion == "Oa":
            item_criterion = AchievementPointsItemCriterion(criterion)
        elif type_criterion == "OA":
            item_criterion = AchievementItemCriterion(criterion)  # TODO
        elif type_criterion == "Ob":
            item_criterion = AchievementAccountItemCriterion(criterion)  # TODO
        elif type_criterion == "Of":
            item_criterion = MountFamilyItemCriterion(criterion)  # TODO
        elif type_criterion == "OH":
            item_criterion = NewHavenbagItemCriterion(criterion)
        elif type_criterion == "OO":
            item_criterion = AchievementObjectiveValidated(criterion)
        elif type_criterion == "Os":
            item_criterion = SmileyPackItemCriterion(criterion)  # TODO
        elif type_criterion == "OV":
            item_criterion = SubscriptionDurationItemCriterion(criterion)  # TODO
        elif type_criterion == "Ow":
            item_criterion = AllianceItemCriterion(criterion)  # TODO
        elif type_criterion == "Ox":
            item_criterion = AllianceRightsItemCriterion(criterion)  # TODO
        elif type_criterion == "Oz":
            item_criterion = AllianceAvAItemCriterion(criterion)  # TODO
        elif type_criterion == "Pa":
            item_criterion = AlignmentLevelItemCriterion(criterion)  # TODO
        elif type_criterion == "PA":
            item_criterion = SoulStoneItemCriterion(criterion)  # TODO
        elif type_criterion == "Pb":
            item_criterion = FriendlistItemCriterion(criterion)  # TODO
        elif type_criterion == "PB":
            item_criterion = SubareaItemCriterion(criterion)  # TODO
        elif type_criterion == "Pe":
            item_criterion = PremiumAccountItemCriterion(criterion)
        elif type_criterion == "PE":
            item_criterion = EmoteItemCriterion(criterion)  # TODO
        elif type_criterion == "Pf":
            item_criterion = RideItemCriterion(criterion)  # TODO
        elif type_criterion == "Pg":
            item_criterion = GiftItemCriterion(criterion)  # TODO
        elif type_criterion == "PG":
            item_criterion = BreedItemCriterion(criterion)  # TODO
        elif type_criterion in ["Pi", "PI"]:
            item_criterion = SkillItemCriterion(criterion)  # TODO
        elif type_criterion in ["PJ", "Pj"]:
            item_criterion = JobItemCriterion(criterion)  # TODO
        elif type_criterion == "Pk":
            item_criterion = BonusSetItemCriterion(criterion)  # TODO
        elif type_criterion == "PK":
            item_criterion = KamaItemCriterion(criterion)  # TODO
        elif type_criterion == "PL":
            item_criterion = LevelItemCriterion(criterion)  # TODO
        elif type_criterion == "Pl":
            item_criterion = PrestigeLevelItemCriterion(criterion)  # TODO
        elif type_criterion == "Pm":
            item_criterion = MapItemCriterion(criterion)  # TODO
        elif type_criterion == "PN":
            item_criterion = NameItemCriterion(criterion)  # TODO
        elif type_criterion == "PO":
            item_criterion = ObjectItemCriterion(criterion)  # TODO
        elif type_criterion == "Po":
            item_criterion = AreaItemCriterion(criterion)  # TODO
        elif type_criterion in ["Pp", "PP"]:
            item_criterion = PVPRankItemCriterion(criterion)  # TODO
        elif type_criterion == "Pr":
            item_criterion = SpecializationItemCriterion(criterion)  # TODO
        elif type_criterion == "PR":
            item_criterion = MariedItemCriterion(criterion)  # TODO
        elif type_criterion == "Ps":
            item_criterion = AlignmentItemCriterion(criterion)  # TODO
        elif type_criterion == "PS":
            item_criterion = SexItemCriterion(criterion)  # TODO
        elif type_criterion == "PT":
            item_criterion = SpellItemCriterion(criterion)  # TODO
        elif type_criterion == "PU":
            item_criterion = BonesItemCriterion(criterion)  # TODO
        elif type_criterion == "Pw":
            item_criterion = GuildItemCriterion(criterion)  # TODO
        elif type_criterion == "PW":
            item_criterion = WeightItemCriterion(criterion)  # TODO
        elif type_criterion == "Px":
            item_criterion = GuildRightsItemCriterion(criterion)  # TODO
        elif type_criterion == "PX":
            item_criterion = AccountRightsItemCriterion(criterion)  # TODO
        elif type_criterion == "Py":
            item_criterion = GuildLevelItemCriterion(criterion)  # TODO
        elif type_criterion in ["Pz", "PZ"]:
            item_criterion = SubscribeItemCriterion(criterion)  # TODO
        elif type_criterion in ["Qa", "Qc", "Qf"]:
            item_criterion = QuestItemCriterion(criterion)  # TODO
        elif type_criterion == "Qo":
            item_criterion = QuestObjectiveItemCriterion(criterion)  # TODO
        elif type_criterion == "SC":
            item_criterion = ServerTypeItemCriterion(criterion)  # TODO
        elif type_criterion == "Sc":
            item_criterion = StaticCriterionItemCriterion(criterion)  # TODO
        elif type_criterion == "Sd":
            item_criterion = DayItemCriterion(criterion)  # TODO
        elif type_criterion == "SG":
            item_criterion = MonthItemCriterion(criterion)  # TODO
        elif type_criterion == "SI":
            item_criterion = ServerItemCriterion(criterion)  # TODO
        elif type_criterion == "ST":
            item_criterion = ServerSeasonTemporisCriterion(criterion)  # TODO
        elif type_criterion == "Sy":
            item_criterion = CommunityItemCriterion(criterion)  # TODO
        else:
            raise ValueError(f"Invalid type criterion : {type_criterion}")

        return item_criterion
