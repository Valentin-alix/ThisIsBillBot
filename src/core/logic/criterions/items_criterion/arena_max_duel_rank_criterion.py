from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.player_state import PlayerState


class ArenaMaxDuelRankCriterion(ItemCriterion):
    def get_criterion(self, player_state: PlayerState, *args, **kwargs) -> int:
        max_rank: int = 0
        if frame.arenaRankDuelInfos and frame.arenaRankDuelInfos.maxRank > max_rank:
            max_rank = frame.arenaRankDuelInfos.maxRank
        return max_rank
