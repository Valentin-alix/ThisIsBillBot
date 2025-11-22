from dataclasses import dataclass

from DBDofusUnity.datas.protos.non_obf.game.game_action_pb2 import GameActionFightEvent
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_move_behavior import MapMoveError


@dataclass
class FightListenerBehavior(Behavior):
    def register_fight_death_check(self) -> None:
        self.event_manager.on(
            GameActionFightEvent,
            self._on_fight_death_check,
            originator=self,
        )

    def _on_fight_death_check(self, msg: GameActionFightEvent) -> None:
        if msg.HasField("death") and (msg.death.target_id == self.game_state.player.character_id):
            self.finish(MapMoveError.PLAYER_DEAD)
