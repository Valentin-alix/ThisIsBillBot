from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from com.ankama.dofus.server.game.protocol.interactive.element_pb2 import (
    StatedElementUpdatedEvent,
)
from src.core.handlers.handler import Handler
from src.core.states.interactive_state import InteractiveState, InteractiveElementInfo


@dataclass
class InteractiveHandler(Handler):
    interactive_state: InteractiveState

    def __post_init__(self):
        self.msg_event.received_game_msg.connect(
            self.on_map_complementary_information_event,
            MapComplementaryInformationEvent,
        )
        self.msg_event.received_game_msg.connect(
            self.on_stated_element_updated_event, StatedElementUpdatedEvent
        )

    def on_map_complementary_information_event(
        self, _, message: MapComplementaryInformationEvent
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

    def on_stated_element_updated_event(self, _, message: StatedElementUpdatedEvent):
        self.interactive_state.interactive_elements_by_id[
            message.stated_element.element_id
        ].state = message.stated_element.state
