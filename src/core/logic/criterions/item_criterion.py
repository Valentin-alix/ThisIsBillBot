from dataclasses import dataclass, field

from src.core.logic.criterions.interface_item_criterion import IItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator
from src.core.logic.stats.stat_id import StatIds
from src.core.states.entity_state import EntityState
from src.core.states.player_state import PlayerState


@dataclass
class ItemCriterion(IItemCriterion):
    criterion: str

    item_operator: ItemCriterionOperator | None = field(init=False, default=None)
    criterion_ref: str = field(init=False, default="")
    criterion_value: int = field(init=False, default=0)
    criterion_value_text: str = field(init=False, default="")

    def __post_init__(self):
        self.get_infos()

    def is_respected(
        self, player_state: PlayerState, entity_state: EntityState
    ) -> bool:
        return self.item_operator.compare(
            self.get_criterion(player_state, entity_state), self.criterion_value
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
        self, player_state: PlayerState, entity_state: EntityState
    ) -> int:
        criterion: int = 0

        stats: list = []

        if stats is None:
            return 0

        elif self.criterion_ref == "Ca":
            criterion = stats.getStatBaseValue(StatIds.AGILITY)

        elif self.criterion_ref == "CA":
            criterion = stats.getStatTotalValue(StatIds.AGILITY)

        elif self.criterion_ref == "Cc":
            criterion = stats.getStatBaseValue(StatIds.CHANCE)

        elif self.criterion_ref == "CC":
            criterion = stats.getStatTotalValue(StatIds.CHANCE)

        elif self.criterion_ref == "Ce":
            criterion = stats.getStatBaseValue(StatIds.ENERGY_POINTS)

        elif self.criterion_ref == "CE":
            criterion = stats.getStatTotalValue(StatIds.MAX_ENERGY_POINTS)

        elif self.criterion_ref == "CH":
            criterion = stats.getStatTotalValue(StatIds.HONOUR_POINTS)

        elif self.criterion_ref == "Ci":
            criterion = stats.getStatBaseValue(StatIds.INTELLIGENCE)

        elif self.criterion_ref == "CI":
            criterion = stats.getStatTotalValue(StatIds.INTELLIGENCE)

        elif self.criterion_ref == "CL":
            criterion = stats.getHealthPoints()

        elif self.criterion_ref == "CM":
            criterion = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS)

        elif self.criterion_ref == "CP":
            criterion = stats.getStatTotalValue(StatIds.ACTION_POINTS)

        elif self.criterion_ref == "Cs":
            criterion = stats.getStatBaseValue(StatIds.STRENGTH)

        elif self.criterion_ref == "CS":
            criterion = stats.getStatTotalValue(StatIds.STRENGTH)

        elif self.criterion_ref == "Cv":
            criterion = stats.getStatBaseValue(StatIds.VITALITY)

        elif self.criterion_ref == "CV":
            criterion = stats.getStatTotalValue(StatIds.VITALITY)

        elif self.criterion_ref == "Cw":
            criterion = stats.getStatBaseValue(StatIds.WISDOM)

        elif self.criterion_ref == "CW":
            criterion = stats.getStatTotalValue(StatIds.WISDOM)

        elif self.criterion_ref == "Ct":
            criterion = stats.getStatTotalValue(StatIds.TACKLE_EVADE)

        elif self.criterion_ref == "CT":
            criterion = stats.getStatTotalValue(StatIds.TACKLE_BLOCK)

        elif self.criterion_ref == "ca":
            criterion = stats.getStatAdditionalValue(StatIds.AGILITY)

        elif self.criterion_ref == "cc":
            criterion = stats.getStatAdditionalValue(StatIds.CHANCE)

        elif self.criterion_ref == "ci":
            criterion = stats.getStatAdditionalValue(StatIds.INTELLIGENCE)

        elif self.criterion_ref == "cs":
            criterion = stats.getStatAdditionalValue(StatIds.STRENGTH)

        elif self.criterion_ref == "cv":
            criterion = stats.getStatAdditionalValue(StatIds.VITALITY)

        elif self.criterion_ref == "cw":
            criterion = stats.getStatAdditionalValue(StatIds.WISDOM)

        return criterion
