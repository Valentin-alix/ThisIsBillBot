from dataclasses import dataclass

from db_dofus_unity.protos.game.gamemap_pb2 import MapComplementaryInformationEvent
from db_dofus_unity.protos.game.interactive_element_pb2 import StatedElementUpdatedEvent
from src.common.logger import Logger
from src.core.frames.frame import Frame
from src.core.states.interactive_state import InteractiveState
from src.interfaces.enums.priority import PriorityEnum
from src.interfaces.models.interactive import InteractiveElementInfo


@dataclass
class InteractiveFrame(Frame):
    interactive_state: InteractiveState

    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            priority=PriorityEnum.MAX,
        )
        self.event_manager.on(
            StatedElementUpdatedEvent,
            self.on_stated_element_updated_event,
            priority=PriorityEnum.MAX,
        )

    def on_map_complementary_information_event(
        self, message: MapComplementaryInformationEvent
    ):
        interactive_elements_by_id: dict[int, InteractiveElementInfo] = {}
        for interactive_element in message.interactive_elements:
            interactive_elements_by_id[interactive_element.element_id] = (
                InteractiveElementInfo(state=1, interactive_element=interactive_element)
            )

        for stated_element in message.stated_elements:
            interactive_elements_by_id[stated_element.element_id].state = (
                stated_element.state
            )
        self.interactive_state.interactive_elements_by_id = interactive_elements_by_id

    def on_stated_element_updated_event(self, message: StatedElementUpdatedEvent):
        related_element = self.interactive_state.interactive_elements_by_id.get(
            message.stated_element.element_id
        )
        if related_element is not None:
            related_element.state = message.stated_element.state
        else:
            Logger().warning(
                f"state element with element id {message.stated_element.element_id} not found in registered "
                f"interactive element"
            )
