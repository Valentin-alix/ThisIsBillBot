from dataclasses import dataclass

from src.core.engine.movements.area_infos import AreaInfo
from src.core.states.state import State

CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER: dict[
    tuple[int, int], AreaInfo
] = {}


@dataclass
class AreaState(State): ...
