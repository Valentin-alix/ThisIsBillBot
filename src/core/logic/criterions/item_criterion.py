from dataclasses import dataclass, field

from src.core.logic.criterions.interface_item_criterion import IItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState
from src.interfaces.enums.stat_id import StatIds


@dataclass
class ItemCriterion(IItemCriterion):
    criterion: str

    item_operator: ItemCriterionOperator = field(init=False)
    criterion_ref: str = field(init=False, default="")
    criterion_value: int = field(init=False, default=0)
    criterion_value_text: str = field(init=False, default="")

    def __post_init__(self):
        self.get_infos()

    def is_respected(
        self,
        player_state: PlayerState,
        map_state: MapState,
        quest_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> bool:
        return self.item_operator.compare(
            self.get_criterion(
                player_state, map_state, quest_state, entity_state, inventory_state
            ),
            self.criterion_value,
        )

    def get_infos(self) -> None:
        for operator in ItemCriterionOperator.OPERATORS_LIST:
            if not self.criterion.find(operator) == 2:
                continue

            self.item_operator = ItemCriterionOperator(operator=operator)
            parts = self.criterion.split(operator)
            self.criterion_ref = parts[0]

            try:
                self.criterion_value = int(float(parts[1].replace(",", ".")))
            except ValueError:
                self.criterion_value = 0

            self.criterion_value_text = parts[1]
            break

    def get_criterion(
        self,
        player_state: PlayerState,
        map_state: MapState,
        quest_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> int:
        criterion: int = 0

        if len(player_state.detail_stat_value_by_id.keys()) == 0:
            return 0

        elif self.criterion_ref == "Ca":
            criterion = player_state.detail_stat_value_by_id[StatIds.AGILITY].base

        elif self.criterion_ref == "CA":
            related_state = player_state.detail_stat_value_by_id[StatIds.AGILITY]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "Cc":
            criterion = player_state.detail_stat_value_by_id[StatIds.CHANCE].base

        elif self.criterion_ref == "CC":
            related_state = player_state.detail_stat_value_by_id[StatIds.CHANCE]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "Ce":
            criterion = player_state.detail_stat_value_by_id[StatIds.ENERGY_POINTS].base

        elif self.criterion_ref == "CE":
            related_state = player_state.detail_stat_value_by_id[
                StatIds.MAX_ENERGY_POINTS
            ]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "CH":
            related_state = player_state.detail_stat_value_by_id[StatIds.HONOUR_POINTS]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "Ci":
            criterion = player_state.detail_stat_value_by_id[StatIds.INTELLIGENCE].base

        elif self.criterion_ref == "CI":
            related_state = player_state.detail_stat_value_by_id[StatIds.INTELLIGENCE]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "CM":
            related_state = player_state.detail_stat_value_by_id[
                StatIds.MOVEMENT_POINTS
            ]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "CP":
            related_state = player_state.detail_stat_value_by_id[StatIds.ACTION_POINTS]
            criterion = related_state.base + related_state.additional
        elif self.criterion_ref == "Cs":
            criterion = player_state.detail_stat_value_by_id[StatIds.STRENGTH].base

        elif self.criterion_ref == "CS":
            related_state = player_state.detail_stat_value_by_id[StatIds.STRENGTH]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "Cv":
            criterion = player_state.detail_stat_value_by_id[StatIds.VITALITY].base

        elif self.criterion_ref == "CV":
            related_state = player_state.detail_stat_value_by_id[StatIds.VITALITY]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "Cw":
            criterion = player_state.detail_stat_value_by_id[StatIds.WISDOM].base

        elif self.criterion_ref == "CW":
            related_state = player_state.detail_stat_value_by_id[StatIds.WISDOM]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "Ct":
            related_state = player_state.detail_stat_value_by_id[StatIds.TACKLE_EVADE]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "CT":
            related_state = player_state.detail_stat_value_by_id[StatIds.TACKLE_BLOCK]
            criterion = related_state.base + related_state.additional

        elif self.criterion_ref == "ca":
            criterion = player_state.detail_stat_value_by_id[StatIds.AGILITY].additional

        elif self.criterion_ref == "cc":
            criterion = player_state.detail_stat_value_by_id[StatIds.CHANCE].additional

        elif self.criterion_ref == "ci":
            criterion = player_state.detail_stat_value_by_id[
                StatIds.INTELLIGENCE
            ].additional

        elif self.criterion_ref == "cs":
            criterion = player_state.detail_stat_value_by_id[
                StatIds.STRENGTH
            ].additional

        elif self.criterion_ref == "cv":
            criterion = player_state.detail_stat_value_by_id[
                StatIds.VITALITY
            ].additional

        elif self.criterion_ref == "cw":
            criterion = player_state.detail_stat_value_by_id[StatIds.WISDOM].additional

        return criterion
