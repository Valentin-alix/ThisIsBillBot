from dataclasses import dataclass

from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import MapMovementRequest
from src.core.behaviors.behavior import Behavior


@dataclass
class FakeBadMovementBehavior(Behavior):
    def run(self):
        bad_movement = MapMovementRequest(
            key_cells=[9999, 8888, 7777], map_id=self.game_state.map.map_id
        )
        self.event_manager.send(bad_movement)
        self.finish()
