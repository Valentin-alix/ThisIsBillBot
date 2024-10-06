from dataclasses import dataclass, field

from db_dofus_unity.protos.game.common_pb2 import InteractiveElement, StatedElement
from src.core.states.state import State


@dataclass
class InteractiveState(State):
    interactive_element_by_id: dict[int, InteractiveElement] = field(
        init=False, default_factory=dict
    )
    stated_element_by_id: dict[int, StatedElement] = field(
        init=False, default_factory=dict
    )
