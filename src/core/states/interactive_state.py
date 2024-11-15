from dataclasses import dataclass, field
from typing import Iterable

from d3_mapping.resources.protos.game.common_pb2 import (
    InteractiveElement,
    StatedElement,
)
from data_center.data_reader import DataReader

from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.core.states.state import State
from src.interfaces.models.collectable import Collectable
from src.signals.grid_signals import GridSignals


class StatedElementByIdDict(dict[int, tuple[StatedElement, Collectable | None]]):
    def __init__(self, cell_id: int, grid_signals: GridSignals):
        self.cell_id = cell_id
        self.grid_signals = grid_signals
        super().__init__()

    def __setitem__(self, key: int, value: tuple[StatedElement, Collectable | None]):
        res = super().__setitem__(key, value)
        self.grid_signals.set_stated_element_on_cell_id.emit(
            self.cell_id, value[0], value[1]
        )
        return res

    def __delitem__(self, key: int):
        res = super().__delitem__(key)
        if len(self) == 0:
            self.grid_signals.set_stated_element_on_cell_id.emit(
                self.cell_id, None, None
            )
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
    player_state: PlayerState
    map_state: MapState
    interactive_element_by_id: dict[int, InteractiveElement] = field(
        init=False, default_factory=dict
    )
    stated_element_by_id: dict[int, tuple[StatedElement, Collectable | None]] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self) -> None:
        self.stated_element_by_cell_id = StatedElementByCellIdDict(self.grid_signals)

    def clear_state(self):
        self.clear_stated_elements()
        self.interactive_element_by_id.clear()

    def clear_stated_elements(self) -> None:
        for stated_element, _ in list(self.stated_element_by_id.values()):
            del self.stated_element_by_id[stated_element.element_id]
            del self.stated_element_by_cell_id[stated_element.cell_id][
                stated_element.element_id
            ]

    def set_stated_elements(self, stated_elements: Iterable[StatedElement]) -> None:
        self.clear_stated_elements()
        for stated_element in stated_elements:
            if not stated_element.on_current_map:
                continue

            collectable = self.get_stated_element_collectable(stated_element)
            self.stated_element_by_id[stated_element.element_id] = (
                stated_element,
                collectable,
            )
            self.stated_element_by_cell_id[stated_element.cell_id][
                stated_element.element_id
            ] = (stated_element, collectable)

    def set_stated_element(self, stated_element: StatedElement) -> None:
        if stated_element.element_id in self.stated_element_by_id:
            del self.stated_element_by_id[stated_element.element_id]
            del self.stated_element_by_cell_id[stated_element.cell_id][
                stated_element.element_id
            ]

        collectable = self.get_stated_element_collectable(stated_element)
        self.stated_element_by_id[stated_element.element_id] = (
            stated_element,
            collectable,
        )
        self.stated_element_by_cell_id[stated_element.cell_id][
            stated_element.element_id
        ] = (stated_element, collectable)

    def get_farmable_collectables(
        self, excluded_element_ids: set[int] | None = None
    ) -> list[Collectable]:
        farmable_collectables: list[Collectable] = []
        for stated_element, collectable in self.stated_element_by_id.values():
            if (
                excluded_element_ids is not None
                and stated_element.element_id in excluded_element_ids
            ):
                continue
            if not collectable:
                continue
            farmable_collectables.append(collectable)

        return farmable_collectables

    def get_stated_element_collectable(
        self, stated_element: StatedElement
    ) -> Collectable | None:
        if stated_element.state != 0:
            return None
        related_interactive = self.interactive_element_by_id.get(
            stated_element.element_id
        )
        if (
            not related_interactive
            or related_interactive.on_current_map is not True
            or len(related_interactive.enabled_skills) == 0
        ):
            return None

        skill = related_interactive.enabled_skills[0]
        data_skill = DataReader().skill_by_id[skill.skill_id]
        if data_skill.gatheredRessourceItem in [-1, 0]:
            return None

        collectable = Collectable(
            map_id=self.map_state.map_id,
            interactive_element=related_interactive,
            skill=skill,
            resource_item_id=data_skill.gatheredRessourceItem,
        )
        if not collectable.is_farmable(
            self.player_state.jobs_lvl_by_id.get(data_skill.parentJobId, 1)
        ):
            return None

        return collectable
