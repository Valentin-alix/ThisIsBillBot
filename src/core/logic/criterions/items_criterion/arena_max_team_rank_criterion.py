from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.player_state import PlayerState


class ArenaMaxTeamRankCriterion(ItemCriterion):
    def get_criterion(self, player_state: PlayerState, *args, **kwargs) -> int:
        frame = Kernel().partyFrame
        max_rank: int = 0
        if frame.arenaRankGroupInfos and frame.arenaRankGroupInfos.maxRank > max_rank:
            max_rank = frame.arenaRankGroupInfos.maxRank
        return max_rank
