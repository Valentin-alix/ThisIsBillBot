from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator
from src.core.repositories.data_reader import DataReader
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState


class AreaItemCriterion(ItemCriterion):

    def is_respected(
        self,
        player_state: PlayerState,
        map_state: MapState,
        quest_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> bool:
        if (
            self.item_operator.text == ItemCriterionOperator.EQUAL
            or self.item_operator.text == ItemCriterionOperator.DIFFERENT
        ):
            return super().is_respected(
                player_state, map_state, quest_state, entity_state, inventory_state
            )
        else:
            return False

    def get_criterion(
        self,
        player_state: PlayerState,
        map_state: MapState,
        quest_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> int:
        return DataReader().sub_area_by_id[map_state.subarea_id].areaId
