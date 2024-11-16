from dataclasses import dataclass

from src.core.engine.movements.area_infos import AreaInfo
from src.core.states.state import State


@dataclass
class AreaState(State): ...


CURRENT_AREAS_PLAYING_INFOS_BY_CHARACTER_ID: dict[int, AreaInfo] = {}
