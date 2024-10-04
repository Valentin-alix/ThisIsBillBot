from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.player_state import PlayerState


class ArenaDuelRankCriterion(ItemCriterion):
    def get_criterion(self, player_state: PlayerState, *args, **kwargs) -> int:
        rank: int = 0
        if frame.arenaRankDuelInfos and frame.arenaRankDuelInfos.rank > rank:
            rank = frame.arenaRankDuelInfos.rank
        return rank
