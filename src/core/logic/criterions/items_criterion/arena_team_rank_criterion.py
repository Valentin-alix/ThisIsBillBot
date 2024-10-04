from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.player_state import PlayerState


class ArenaTeamRankCriterion(ItemCriterion):
    def get_criterion(self, player_state: PlayerState, *args, **kwargs) -> int:
        frame = Kernel().partyFrame
        rank: int = 0
        if frame.arenaRankGroupInfos and frame.arenaRankGroupInfos.rank > rank:
            rank = frame.arenaRankGroupInfos.rank
        return rank
