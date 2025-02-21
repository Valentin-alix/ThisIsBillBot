from dataclasses import dataclass, field
from typing import Callable

from dofus_unity_reader.enums.characteristic_enum import CharacteristicEnum

from src.core.engine.contexts import CriterionContext
from src.core.engine.movements.world.criterions.interface_item_criterion import (
    IItemCriterion,
)
from src.core.engine.movements.world.criterions.item_criterion_operator import (
    ItemCriterionOperator,
)


def _get_criterion_handlers() -> dict[str, Callable[[CriterionContext], int]]:
    return {
        "Ca": lambda gs: (
            gs.fight_characteristic_by_id[CharacteristicEnum.AGILITY].detailed.base
        ),
        "CA": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.AGILITY]
            ).detailed.base
            + s.detailed.additional
        ),
        "Cc": lambda gs: (
            gs.fight_characteristic_by_id[CharacteristicEnum.CHANCE].detailed.base
        ),
        "CC": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.CHANCE]
            ).detailed.base
            + s.detailed.additional
        ),
        "Ce": lambda gs: (
            gs.fight_characteristic_by_id[
                CharacteristicEnum.ENERGY_POINTS
            ].detailed.base
        ),
        "CE": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.MAX_ENERGY_POINTS]
            ).detailed.base
            + s.detailed.additional
        ),
        "CH": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.HONOUR_POINTS]
            ).detailed.base
            + s.detailed.additional
        ),
        "Ci": lambda gs: (
            gs.fight_characteristic_by_id[CharacteristicEnum.INTELLIGENCE].detailed.base
        ),
        "CI": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.INTELLIGENCE]
            ).detailed.base
            + s.detailed.additional
        ),
        "CM": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.MOVEMENT_POINTS]
            ).detailed.base
            + s.detailed.additional
        ),
        "CP": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.ACTION_POINTS]
            ).detailed.base
            + s.detailed.additional
        ),
        "Cs": lambda gs: (
            gs.fight_characteristic_by_id[CharacteristicEnum.STRENGTH].detailed.base
        ),
        "CS": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.STRENGTH]
            ).detailed.base
            + s.detailed.additional
        ),
        "Cv": lambda gs: (
            gs.fight_characteristic_by_id[CharacteristicEnum.VITALITY].detailed.base
        ),
        "CV": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.VITALITY]
            ).detailed.base
            + s.detailed.additional
        ),
        "Cw": lambda gs: (
            gs.fight_characteristic_by_id[CharacteristicEnum.WISDOM].detailed.base
        ),
        "CW": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.WISDOM]
            ).detailed.base
            + s.detailed.additional
        ),
        "Ct": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.TACKLE_EVADE]
            ).detailed.base
            + s.detailed.additional
        ),
        "CT": lambda gs: (
            (
                s := gs.fight_characteristic_by_id[CharacteristicEnum.TACKLE_BLOCK]
            ).detailed.base
            + s.detailed.additional
        ),
        "ca": lambda gs: (
            gs.fight_characteristic_by_id[
                CharacteristicEnum.AGILITY
            ].detailed.additional
        ),
        "cc": lambda gs: (
            gs.fight_characteristic_by_id[CharacteristicEnum.CHANCE].detailed.additional
        ),
        "ci": lambda gs: (
            gs.fight_characteristic_by_id[
                CharacteristicEnum.INTELLIGENCE
            ].detailed.additional
        ),
        "cs": lambda gs: (
            gs.fight_characteristic_by_id[
                CharacteristicEnum.STRENGTH
            ].detailed.additional
        ),
        "cv": lambda gs: (
            gs.fight_characteristic_by_id[
                CharacteristicEnum.VITALITY
            ].detailed.additional
        ),
        "cw": lambda gs: (
            gs.fight_characteristic_by_id[CharacteristicEnum.WISDOM].detailed.additional
        ),
    }


CRITERION_HANDLERS = _get_criterion_handlers()


@dataclass
class ItemCriterion(IItemCriterion):
    criterion: str

    item_operator: ItemCriterionOperator = field(init=False)
    criterion_ref: str = field(init=False, default="")
    criterion_value: int = field(init=False, default=0)
    criterion_value_text: str = field(init=False, default="")

    def __post_init__(self):
        self.get_infos()

    def is_respected(self, context: CriterionContext) -> bool:
        return self.item_operator.compare(
            self.get_criterion(context),
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

    def get_criterion(self, context: CriterionContext) -> int:
        if len(context.fight_characteristic_by_id.keys()) == 0:
            return 0

        handler = CRITERION_HANDLERS.get(self.criterion_ref)
        if handler is None:
            return 0

        return handler(context)
