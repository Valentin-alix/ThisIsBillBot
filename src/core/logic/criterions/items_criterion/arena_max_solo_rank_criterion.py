from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.player_state import PlayerState


class ArenaMaxSoloRankCriterion(ItemCriterion):
    def get_criterion(self, player_state: PlayerState, *args, **kwargs) -> int:
        frame: PartyManagementFrame = Kernel().worker.getFrame("PartyManagementFrame")
        return int(frame.arenaRankSoloInfos.maxRank)
