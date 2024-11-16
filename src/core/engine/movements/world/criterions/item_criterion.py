from dataclasses import dataclass, field

from D3Database.enums.characteristic_enum import CharacteristicEnum
from src.core.engine.movements.world.criterions.interface_item_criterion import (
    IItemCriterion,
)
from src.core.engine.movements.world.criterions.item_criterion_operator import (
    ItemCriterionOperator,
)
from src.core.states.game_state import GameState


@dataclass
class ItemCriterion(IItemCriterion):
    criterion: str

    item_operator: ItemCriterionOperator = field(init=False)
    criterion_ref: str = field(init=False, default="")
    criterion_value: int = field(init=False, default=0)
    criterion_value_text: str = field(init=False, default="")

    def __post_init__(self):
        self.get_infos()

    def is_respected(self, game_state: GameState) -> bool:
        return self.item_operator.compare(
            self.get_criterion(game_state),
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

    def get_criterion(self, game_state: GameState) -> int:
        criterion: int = 0

        if len(game_state.fight.characteristic_by_id.keys()) == 0:
            return 0

        elif self.criterion_ref == "Ca":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.AGILITY
            ].detailed.base

        elif self.criterion_ref == "CA":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.AGILITY
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "Cc":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.CHANCE
            ].detailed.base

        elif self.criterion_ref == "CC":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.CHANCE
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "Ce":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.ENERGY_POINTS
            ].detailed.base

        elif self.criterion_ref == "CE":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.MAX_ENERGY_POINTS
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "CH":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.HONOUR_POINTS
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "Ci":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.INTELLIGENCE
            ].detailed.base

        elif self.criterion_ref == "CI":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.INTELLIGENCE
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "CM":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.MOVEMENT_POINTS
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "CP":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.ACTION_POINTS
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional
        elif self.criterion_ref == "Cs":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.STRENGTH
            ].detailed.base

        elif self.criterion_ref == "CS":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.STRENGTH
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "Cv":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.VITALITY
            ].detailed.base

        elif self.criterion_ref == "CV":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.VITALITY
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "Cw":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.WISDOM
            ].detailed.base

        elif self.criterion_ref == "CW":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.WISDOM
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "Ct":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.TACKLE_EVADE
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "CT":
            related_state = game_state.fight.characteristic_by_id[
                CharacteristicEnum.TACKLE_BLOCK
            ]
            criterion = related_state.detailed.base + related_state.detailed.additional

        elif self.criterion_ref == "ca":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.AGILITY
            ].detailed.additional

        elif self.criterion_ref == "cc":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.CHANCE
            ].detailed.additional

        elif self.criterion_ref == "ci":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.INTELLIGENCE
            ].detailed.additional

        elif self.criterion_ref == "cs":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.STRENGTH
            ].detailed.additional

        elif self.criterion_ref == "cv":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.VITALITY
            ].detailed.additional

        elif self.criterion_ref == "cw":
            criterion = game_state.fight.characteristic_by_id[
                CharacteristicEnum.WISDOM
            ].detailed.additional

        return criterion
