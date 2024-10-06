from dataclasses import dataclass

from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.repositories.data_reader import DataReader
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState


@dataclass
class QuestItemCriterion(ItemCriterion):
    criterion: str

    def is_respected(
        self,
        player_state: PlayerState,
        map_state: MapState,
        quest_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> bool:
        quest = DataReader().quest_objective_by_id.get(self.criterion_value)
        if not quest:
            return False
        if self.criterion_ref == "Qa":
            return quest.id in quest_state.active_quest_by_id
        if self.criterion_ref == "Qc":
            return True
        if self.criterion_ref == "Qf":
            return quest.id in quest_state.finished_quest_by_id
        return False


if __name__ == "__main__":
    temp = QuestItemCriterion(criterion="Qf=1477")
