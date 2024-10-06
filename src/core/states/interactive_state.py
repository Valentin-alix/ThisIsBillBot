from dataclasses import dataclass, field
from typing import Iterable

from db_dofus_unity.protos.game.common_pb2 import InteractiveElement, StatedElement
from src.core.states.state import State
from src.signals.grid_signals import GridSignals


class StatedElementByCellIdDict(dict[int, StatedElement]):
    def __init__(self, grid_signals: GridSignals):
        self.grid_signals = grid_signals
        super().__init__()

    def __setitem__(self, key: int, value: StatedElement):
        self.grid_signals.set_stated_element_on_cell_id.emit(key, True)
        return super().__setitem__(key, value)

    def __delitem__(self, key: int):
        self.grid_signals.set_stated_element_on_cell_id.emit(key, False)
        return super().__delitem__(key)


@dataclass
class InteractiveState(State):
    grid_signals: GridSignals
    interactive_element_by_id: dict[int, InteractiveElement] = field(
        init=False, default_factory=dict
    )
    stated_element_by_id: dict[int, StatedElement] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self):
        self.stated_element_by_cell_id = StatedElementByCellIdDict(self.grid_signals)

    def clear_stated_elements(self):
        for stated_element in list(self.stated_element_by_id.values()):
            del self.stated_element_by_id[stated_element.element_id]
            del self.stated_element_by_cell_id[stated_element.cell_id]

    def set_stated_elements(self, stated_elements: Iterable[StatedElement]):
        self.clear_stated_elements()
        for stated_element in stated_elements:
            self.stated_element_by_id[stated_element.element_id] = stated_element
            self.stated_element_by_cell_id[stated_element.cell_id] = stated_element

    def set_stated_element(self, stated_element: StatedElement):
        if stated_element.element_id in self.stated_element_by_id:
            del self.stated_element_by_id[stated_element.element_id]
            del self.stated_element_by_cell_id[stated_element.cell_id]

        self.stated_element_by_id[stated_element.element_id] = stated_element
        self.stated_element_by_cell_id[stated_element.cell_id] = stated_element
