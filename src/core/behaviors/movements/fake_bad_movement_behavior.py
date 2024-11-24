from dataclasses import dataclass

from d3_database.protos.non_obf.game.gamemap_pb2 import MapMovementRequest
from src.core.behaviors.behavior import Behavior


@dataclass
class FakeBadMovementBehavior(Behavior):
    def run(self):
        bad_movement = MapMovementRequest(
            key_cells=[9999, 8888, 7777], map_id=self.game_state.map.map_id
        )
        self.event_manager.send(bad_movement)
        self.finish()
