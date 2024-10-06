from dataclasses import dataclass

from src.core.behaviors.behavior import Behavior, EndCode
from src.core.behaviors.fight.fight_placement_behavior import FightPlacementBehavior
from src.core.states.fight_state import FightState
from src.core.states.player_state import PlayerState


@dataclass
class FightBehavior(Behavior):
    player_state: PlayerState
    fight_state: FightState
    fight_placement_behavior: FightPlacementBehavior

    def run(self):
        self.fight_placement_behavior.start(callback=self.on_fight_placed, parent=self)

    def on_fight_placed(self, code: EndCode):
        print("character is placed")
