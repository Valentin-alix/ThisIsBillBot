from dataclasses import dataclass

from db_dofus_unity.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapCurrentEvent,
)
from db_dofus_unity.protos.game.interactive_element_pb2 import (
    InteractiveMapUpdateEvent,
    InteractiveElementUpdatedEvent,
    StatedMapUpdateEvent,
    StatedElementUpdatedEvent,
)
from src.core.frames.frame import Frame
from src.core.states.interactive_state import InteractiveState


@dataclass
class InteractiveFrame(Frame):
    interactive_state: InteractiveState

    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            originator=self,
        )
        self.event_manager.on(
            InteractiveMapUpdateEvent,
            self.on_interactive_map_update_event,
            originator=self,
        )
        self.event_manager.on(
            InteractiveElementUpdatedEvent,
            self.on_interactive_element_updated_event,
            originator=self,
        )
        self.event_manager.on(
            StatedMapUpdateEvent, self.on_stated_map_update_event, originator=self
        )
        self.event_manager.on(
            StatedElementUpdatedEvent,
            self.on_stated_element_updated_event,
            originator=self,
        )
        self.event_manager.on(
            MapCurrentEvent, self.on_map_current_event, originator=self
        )

    def on_map_complementary_information_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.interactive_state.interactive_element_by_id = {
            element.element_id: element for element in message.interactive_elements
        }
        self.interactive_state.set_stated_elements(message.stated_elements)

    def on_interactive_map_update_event(self, msg: InteractiveMapUpdateEvent):
        self.interactive_state.interactive_element_by_id = {
            element.element_id: element for element in msg.interactive_elements
        }

    def on_interactive_element_updated_event(self, msg: InteractiveElementUpdatedEvent):
        self.interactive_state.interactive_element_by_id[
            msg.interactive_element.element_id
        ] = msg.interactive_element

    def on_stated_map_update_event(self, msg: StatedMapUpdateEvent):
        self.interactive_state.set_stated_elements(msg.stated_elements)

    def on_stated_element_updated_event(self, msg: StatedElementUpdatedEvent):
        self.interactive_state.set_stated_element(msg.stated_element)

    def on_map_current_event(self, msg: MapCurrentEvent):
        self.interactive_state.clear_stated_elements()
