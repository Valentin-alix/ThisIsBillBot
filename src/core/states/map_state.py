import dataclasses
from dataclasses import dataclass

from src.core.states.state import State


@dataclass
class MapState(State):
    subarea_id: int = dataclasses.field(init=False, default=0)
    map_id: int = dataclasses.field(init=False, default=0)
    has_aggressive_monsters: bool = dataclasses.field(init=False, default=False)
