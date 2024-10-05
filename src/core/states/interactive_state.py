from dataclasses import dataclass, field

from src.core.states.state import State
from src.interfaces.models.interactive import InteractiveElementInfo


@dataclass
class InteractiveState(State):
    interactive_elements_by_id: dict[int, InteractiveElementInfo] = field(
        init=False, default_factory=lambda: {}
    )
