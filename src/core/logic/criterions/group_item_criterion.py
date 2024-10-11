from dataclasses import dataclass, field

from src.core.logic.criterions.interface_item_criterion import IItemCriterion
from src.core.logic.criterions.item_criterion_factory import ItemCriterionFactory
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.game_state import GameState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import MapSignals


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


if __name__ == "__main__":
    grid_signals = GridSignals()
    debug_signals = MapSignals()
    game_info_signals = GameInfoSignals()

    map_state = MapState(grid_signals=grid_signals)
    entity_state = EntityState(grid_signals=grid_signals)
    interactive_state = InteractiveState(grid_signals=grid_signals)
    player_state = PlayerState(
        game_info_signals=game_info_signals,
        interactive_state=interactive_state,
        entity_state=entity_state,
        map_state=map_state,
    )
    fight_state = FightState(
        game_info_signals=game_info_signals, player_state=player_state
    )
    player_state = PlayerState(
        map_state=map_state,
        game_info_signals=game_info_signals,
        entity_state=entity_state,
        interactive_state=interactive_state,
    )
    quest_state = ObjectiveState()
    inventory_state = InventoryState(game_info_signals=game_info_signals)

    criterion = GroupItemCriterion("MI=515576,1")
