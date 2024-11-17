from dataclasses import dataclass, field
from typing import Iterable

from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import InteractiveElement, StatedElement
from src.core.engine.interactives.collectable import Collectable, get_stated_element_collectable
from src.core.signals.grid_signals import GridSignals
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.core.states.state import State


class StatedElementByIdDict(dict[int, tuple[StatedElement, Collectable | None]]):
    def __init__(self, cell_id: int):
        self.cell_id = cell_id
        super().__init__()


class StatedElementByCellIdDict(dict[int, StatedElementByIdDict]):
    def __missing__(self, key) -> StatedElementByIdDict:
        value = StatedElementByIdDict(cell_id=key)
        self.__setitem__(key, value)
        return value


@dataclass
class InteractiveState(State):
    grid_signals: GridSignals
    player_state: PlayerState
    map_state: MapState
    interactive_element_by_id: dict[int, InteractiveElement] = field(init=False, default_factory=dict)
    stated_element_by_id: dict[int, tuple[StatedElement, Collectable | None]] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self.stated_element_by_cell_id: StatedElementByCellIdDict = StatedElementByCellIdDict()

    def clear_state(self):
        self.clear_stated_elements()
        self.interactive_element_by_id.clear()

    def clear_stated_elements(self) -> None:
        if not self.stated_element_by_id:
            return
        batch = [(stated_element.cell_id, None, None) for stated_element, _ in self.stated_element_by_id.values()]
        self.stated_element_by_id.clear()
        self.stated_element_by_cell_id.clear()
        if batch:
            self.grid_signals.set_stated_element_on_cell_id_batch.emit(batch)

    def set_stated_elements(self, stated_elements: Iterable[StatedElement]) -> None:
        old_cell_ids = {se.cell_id for se, _ in self.stated_element_by_id.values()}
        self.stated_element_by_id.clear()
        self.stated_element_by_cell_id.clear()
        batch: list[tuple[int, StatedElement | None, Collectable | None]] = []
        new_cell_ids: set[int] = set()
        for stated_element in stated_elements:
            if not stated_element.on_current_map:
                continue
            collectable = self.get_stated_element_collectable(stated_element)
            self.stated_element_by_id[stated_element.element_id] = (
                stated_element,
                collectable,
            )
            self.stated_element_by_cell_id[stated_element.cell_id][stated_element.element_id] = (
                stated_element,
                collectable,
            )
            new_cell_ids.add(stated_element.cell_id)
            batch.append((stated_element.cell_id, stated_element, collectable))
        for old_cell_id in old_cell_ids - new_cell_ids:
            batch.append((old_cell_id, None, None))
        if batch:
            self.grid_signals.set_stated_element_on_cell_id_batch.emit(batch)

    def set_stated_element(self, stated_element: StatedElement) -> None:
        old_cell_id = None
        if stated_element.element_id in self.stated_element_by_id:
            old_se, _ = self.stated_element_by_id[stated_element.element_id]
            old_cell_id = old_se.cell_id
            del self.stated_element_by_id[stated_element.element_id]
            del self.stated_element_by_cell_id[old_cell_id][stated_element.element_id]

        collectable = self.get_stated_element_collectable(stated_element)
        self.stated_element_by_id[stated_element.element_id] = (
            stated_element,
            collectable,
        )
        self.stated_element_by_cell_id[stated_element.cell_id][stated_element.element_id] = (
            stated_element,
            collectable,
        )
        batch: list[tuple[int, StatedElement | None, Collectable | None]] = [
            (stated_element.cell_id, stated_element, collectable)
        ]
        if old_cell_id is not None and old_cell_id != stated_element.cell_id:
            remaining = self.stated_element_by_cell_id.get(old_cell_id)
            if not remaining or len(remaining) == 0:
                batch.append((old_cell_id, None, None))
        self.grid_signals.set_stated_element_on_cell_id_batch.emit(batch)

    def get_farmable_collectables(self, excluded_element_ids: set[int] | None = None) -> list[Collectable]:
        farmable_collectables: list[Collectable] = []
        for stated_element, collectable in self.stated_element_by_id.values():
            if excluded_element_ids is not None and stated_element.element_id in excluded_element_ids:
                continue
            if not collectable:
                continue
            farmable_collectables.append(collectable)

        return farmable_collectables

    def get_stated_element_collectable(self, stated_element: StatedElement) -> Collectable | None:
        return get_stated_element_collectable(
            stated_element,
            self.interactive_element_by_id,
            self.map_state.map_id,
            self.player_state.jobs_lvl_by_id,
        )

    def get_element_and_skill_by_skill_id(self, skill_id: int):
        related_element, related_skill = next(
            (element, skill)
            for element in self.interactive_element_by_id.values()
            if (
                skill := next(
                    (enabled_skill for enabled_skill in element.enabled_skills if enabled_skill.skill_id == skill_id),
                    None,
                )
            )
            is not None
        )
        return related_element, related_skill
