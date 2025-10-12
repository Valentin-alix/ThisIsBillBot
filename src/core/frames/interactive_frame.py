from dataclasses import dataclass

from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.interactive_element_pb2 import (
    InteractiveElementUpdatedEvent,
    InteractiveMapUpdateEvent,
    StatedElementUpdatedEvent,
    StatedMapUpdateEvent,
)
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.game_constants.job import HARVESTER_JOB_IDS, JobEnum

from src.controller.game_data import GameDataController
from src.core.frames.frame import Frame


@dataclass
class InteractiveFrame(Frame):
    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            InteractiveMapUpdateEvent,
            self.on_interactive_map_update_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            StatedMapUpdateEvent,
            self.on_stated_map_update_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            InteractiveElementUpdatedEvent,
            self.on_interactive_element_updated_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            StatedElementUpdatedEvent,
            self.on_stated_element_updated_event,
            originator=self,
            priority=self.priority,
        )

    def on_map_complementary_information_event(self, message: MapComplementaryInformationEvent):
        self.game_state.interactive.interactive_element_by_id = {
            element.element_id: element for element in message.interactive_elements
        }
        self.game_state.interactive.set_stated_elements(message.stated_elements)

        map_id = message.map_id
        if map_id in GameDataController().get_map_ids_checked():
            return

        item_and_job_by_gfx_array: list[tuple[int, int, JobEnum]] = []
        for interactive_element in message.interactive_elements:
            for skill in list(interactive_element.enabled_skills) + list(interactive_element.disabled_skills):
                data_skill = DataReader().skill_by_id[skill.skill_id]
                if (
                    data_skill.gatheredRessourceItem in [-1, 0]
                    or data_skill.parentJobId not in HARVESTER_JOB_IDS
                ):
                    continue
                gfx_id = (
                    MapReader()
                    .get_ref_data_by_element_id_by_map_id(map_id)[interactive_element.element_id]
                    .gfxId
                )
                if gfx_id is None:
                    continue
                item_and_job_by_gfx_array.append(
                    (
                        gfx_id,
                        data_skill.gatheredRessourceItem,
                        JobEnum(data_skill.parentJobId),
                    )
                )
        GameDataController().add_multiple_item_job_by_gfx(item_and_job_by_gfx_array)
        GameDataController().add_map_id_checked(message.map_id)

    def on_interactive_map_update_event(self, msg: InteractiveMapUpdateEvent):
        for interactive_element in msg.interactive_elements:
            self.game_state.interactive.interactive_element_by_id[interactive_element.element_id] = (
                interactive_element
            )

    def on_stated_map_update_event(self, msg: StatedMapUpdateEvent):
        self.game_state.interactive.set_stated_elements(msg.stated_elements)

    def on_interactive_element_updated_event(self, msg: InteractiveElementUpdatedEvent):
        self.game_state.interactive.interactive_element_by_id[msg.interactive_element.element_id] = (
            msg.interactive_element
        )

    def on_stated_element_updated_event(self, msg: StatedElementUpdatedEvent):
        self.game_state.interactive.set_stated_element(msg.stated_element)
