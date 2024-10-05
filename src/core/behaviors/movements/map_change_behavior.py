from dataclasses import dataclass

from db_dofus_unity.protos.game.gamemap_pb2 import (
    MapChangeRequest,
    MapComplementaryInformationEvent,
)
from src.common.logger import Logger
from src.core.behaviors.behavior import Behavior


@dataclass
class MapChangeBehavior(Behavior):
    def run(self, map_id: int):
        Logger().info("Changing map")
        map_change_request = MapChangeRequest(map_id=map_id)
        self.event_manager.send(map_change_request)
        self.event_manager.on(
            MapComplementaryInformationEvent, self.finish, originator=self, once=True
        )
