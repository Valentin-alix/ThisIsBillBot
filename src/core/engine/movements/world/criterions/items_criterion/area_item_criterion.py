from D3Database.data_center.data_reader import DataReader
from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)
from src.core.engine.movements.world.criterions.item_criterion_operator import (
    ItemCriterionOperator,
)
from src.core.states.game_state import GameState


class AreaItemCriterion(ItemCriterion):
    def is_respected(self, game_state: GameState) -> bool:
        if (
            self.item_operator.text == ItemCriterionOperator.EQUAL
            or self.item_operator.text == ItemCriterionOperator.DIFFERENT
        ):
            return super().is_respected(game_state)
        else:
            return False

    def get_criterion(self, game_state: GameState) -> int:
        return DataReader().sub_area_by_id[game_state.map.sub_area_id].areaId
