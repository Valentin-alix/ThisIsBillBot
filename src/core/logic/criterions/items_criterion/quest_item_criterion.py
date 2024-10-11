from dataclasses import dataclass

from src.core.data_center.data_reader import DataReader
from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.game_state import GameState


@dataclass
class QuestItemCriterion(ItemCriterion):
    criterion: str

    def is_respected(self, game_state: GameState) -> bool:
        quest = DataReader().quest_objective_by_id.get(self.criterion_value)
        if not quest:
            return False
        if self.criterion_ref == "Qa":
            return quest.id in game_state.objective.active_quest_by_id
        if self.criterion_ref == "Qc":
            return True
        if self.criterion_ref == "Qf":
            return quest.id in game_state.objective.finished_quest_by_id
        return False


if __name__ == "__main__":
    temp = QuestItemCriterion(criterion="Qf=1477")
