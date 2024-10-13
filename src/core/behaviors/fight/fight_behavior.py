from dataclasses import dataclass

from d3_mapping.resources.protos.game.character_pb2 import CharacterLifeStatusEvent
from d3_mapping.resources.protos.game.fight_pb2 import (
    FightTurnStartPlayingEvent,
)
from d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    FightMapInformationEvent,
)
from src.const import (
    ON_PLAYER_TURN,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.fight.fight_preparation_behavior import FightPreparationBehavior
from src.core.behaviors.fight.fight_turn_behavior import FightTurnBehavior
from src.core.behaviors.fight.revive_behavior import ReviveBehavior
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException


@dataclass
class FightBehavior(Behavior):
    path_finding: Pathfinding
    revive_behavior: ReviveBehavior
    fight_turn_behavior: FightTurnBehavior
    fight_preparation_behavior: FightPreparationBehavior

    def run(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            callback=self.on_map_complementary_information_event,
            originator=self,
            once=True,
        )
        if self.game_state.fight.is_map_fight_initialized:
            self.on_fight_map_initialized()
        else:
            self.event_manager.on(
                FightMapInformationEvent,
                lambda _: self.on_fight_map_initialized(),
                originator=self,
            )

    def on_fight_map_initialized(self):
        self.event_manager.on(
            FightTurnStartPlayingEvent,
            lambda _: self.run_timer(ON_PLAYER_TURN, self.on_player_turn),
            originator=self,
        )
        if self.game_state.fight.is_our_turn:
            self.on_player_turn()
        elif len(self.game_state.fight.fight_placement_possible_positions) != 0:
            self.fight_preparation_behavior.start(
                callback=self.on_fight_preparation_behavior_finish, parent=self
            )

    def on_map_complementary_information_event(
        self, msg: MapComplementaryInformationEvent
    ):
        if (
            self.game_state.player.life_state
            == CharacterLifeStatusEvent.LifeStatus.TOMBSTONE
        ):
            return self.revive_behavior.start(callback=self.finish, parent=self)
        self.finish()

    def on_fight_preparation_behavior_finish(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

    def on_player_turn(self):
        self.fight_turn_behavior.start(callback=None, parent=self)
