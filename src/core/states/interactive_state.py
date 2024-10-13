from dataclasses import dataclass, field
from typing import Iterable

from d3_mapping.resources.protos.game.common_pb2 import (
    StatedElement,
    InteractiveElement,
)
from src.core.states.state import State
from src.signals.grid_signals import GridSignals


class StatedElementByIdDict(dict[int, StatedElement]):
    def __init__(self, cell_id: int, grid_signals: GridSignals):
        self.cell_id = cell_id
        self.grid_signals = grid_signals
        super().__init__()

    def __setitem__(self, key: int, value: StatedElement):
        res = super().__setitem__(key, value)
        self.grid_signals.set_stated_element_on_cell_id.emit(self.cell_id, value.state)
        return res

    def __delitem__(self, key: int):
        res = super().__delitem__(key)
        if len(self) == 0:
            self.grid_signals.set_stated_element_on_cell_id.emit(self.cell_id, None)
        return res


class StatedElementByCellIdDict(dict[int, StatedElementByIdDict]):
    def __init__(self, grid_signals: GridSignals):
        self.grid_signals = grid_signals
        super().__init__()

    def __missing__(self, key) -> StatedElementByIdDict:
        value = StatedElementByIdDict(cell_id=key, grid_signals=self.grid_signals)
        self.__setitem__(key, value)
        return value


@dataclass
class InteractiveState(State):
    grid_signals: GridSignals
    interactive_element_by_id: dict[int, InteractiveElement] = field(
        init=False, default_factory=dict
    )
    stated_element_by_id: dict[int, StatedElement] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self) -> None:
        self.stated_element_by_cell_id = StatedElementByCellIdDict(self.grid_signals)

    def clear_state(self):
        self.clear_stated_elements()
        self.interactive_element_by_id.clear()

    def clear_stated_elements(self) -> None:
        for stated_element in list(self.stated_element_by_id.values()):
            del self.stated_element_by_id[stated_element.element_id]
            del self.stated_element_by_cell_id[stated_element.cell_id][
                stated_element.element_id
            ]

    def set_stated_elements(self, stated_elements: Iterable[StatedElement]) -> None:
        self.clear_stated_elements()
        for stated_element in stated_elements:
            if not stated_element.on_current_map:
                continue

            self.stated_element_by_id[stated_element.element_id] = stated_element
            self.stated_element_by_cell_id[stated_element.cell_id][
                stated_element.element_id
            ] = stated_element

    def set_stated_element(self, stated_element: StatedElement) -> None:
        if stated_element.element_id in self.stated_element_by_id:
            del self.stated_element_by_id[stated_element.element_id]
            del self.stated_element_by_cell_id[stated_element.cell_id][
                stated_element.element_id
            ]

        self.stated_element_by_id[stated_element.element_id] = stated_element
        self.stated_element_by_cell_id[stated_element.cell_id][
            stated_element.element_id
        ] = stated_element
