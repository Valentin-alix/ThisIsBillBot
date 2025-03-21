from dataclasses import dataclass

from dofus_unity_reader.game_constants.map_id import MapIdEnum
from gamemap_pb2 import MapComplementaryInformationEvent
from quest_pb2 import GuideModQuitRequest

from src.core.behaviors.behavior import Behavior
from src.core.config import BIG_RANGE


@dataclass
class TutorialBehavior(Behavior):
    def run(self):
        assert self.game_state.map.map_id == MapIdEnum.TUTORIAL_STARTING_MAP
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            originator=self,
            once=True,
        )
        req = GuideModQuitRequest()
        self.run_timer(BIG_RANGE, lambda: self.event_manager.send(req))

    def on_map_complementary_information_event(
        self, msg: MapComplementaryInformationEvent
    ):
        self.finish()
