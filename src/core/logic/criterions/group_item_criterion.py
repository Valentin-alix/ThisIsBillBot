from dataclasses import dataclass, field

from src.core.logic.criterions.interface_item_criterion import IItemCriterion
from src.core.logic.criterions.item_criterion_factory import ItemCriterionFactory
from src.core.states.game_state import GameState


@dataclass
class GroupItemCriterion(IItemCriterion):
    criterion: str

    items_criterion: list[IItemCriterion | None] = field(
        init=False, default_factory=lambda: []
    )
    operators: list[str] = field(
        init=False, default_factory=lambda: []
    )  # operator between item items_criterion

    def __post_init__(self):
        self.parse()

    def parse(self) -> None:
        position: int = 0
        stack: list[int] = []
        while position < len(self.criterion):
            char = self.criterion[position]
            if char == "(":
                stack.append(position)
                position += 1
            elif char == ")":
                if not stack:
                    raise ValueError(f"Unmatched parenthesis at position {position}")

                start_pos = stack.pop()
                if not stack:
                    group_content = self.criterion[start_pos + 1 : position]
                    nested_group = GroupItemCriterion(group_content)
                    self.items_criterion.append(nested_group)
                position += 1

            elif char in ["&", "|"] and not stack:
                self.operators.append(char)
                position += 1

            else:
                if not stack:
                    criterion_end = self._find_next_operator_or_parenthesis(position)
                    criterion = self.criterion[position:criterion_end].strip()
                    item_criterion = ItemCriterionFactory.create(criterion)
                    self.items_criterion.append(item_criterion)
                    position = criterion_end
                else:
                    position += 1

        if stack:
            raise ValueError(f"Unmatched parenthesis at position {stack.pop()}")

        if len(self.items_criterion) == 0 and position > 0:
            item_criterion = ItemCriterionFactory.create(self.criterion)
            self.items_criterion.append(item_criterion)

        if len(self.items_criterion) == 1:
            top_group = self.items_criterion[0]
            if isinstance(top_group, GroupItemCriterion):
                self.items_criterion = top_group.items_criterion
                self.operators = top_group.operators

    def _find_next_operator_or_parenthesis(self, start_pos: int):
        for pos in range(start_pos, len(self.criterion)):
            if self.criterion[pos] in ["&", "|", "(", ")"]:
                return pos
        return len(self.criterion)

    def is_respected(self, game_state: GameState) -> bool:
        if len(self.items_criterion) == 0:
            return True

        if len(self.items_criterion) == 1:
            item_criterion = self.items_criterion[0]
            if item_criterion is None:
                return False
            return item_criterion.is_respected(game_state)

        if len(self.operators) > 0 and self.operators[0] == "|":
            for criterion in self.items_criterion:
                if criterion is not None and criterion.is_respected(game_state):
                    return True
            return False

        for criterion in self.items_criterion:
            if criterion is None or not criterion.is_respected(game_state):
                return False

        return True
