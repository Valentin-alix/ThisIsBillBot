from dataclasses import dataclass

from datas.protos.non_obf.game.fight_pb2 import (
    FightTurnStartPlayingEvent,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)

from src.core.behaviors.behavior import Behavior, BehaviorState
from src.core.behaviors.farms.fight.fight_preparation_behavior import (
    FightPreparationBehavior,
)
from src.core.behaviors.farms.fight.fight_turn_behavior import FightTurnBehavior
from src.core.config import BETWEEN_ACTION_RANGE
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.signals.shared_farm_signals import SharedSignals

FIGHT_TIMEOUT_SECONDS = 30 * 60


@dataclass
class FightBehavior(Behavior):
    path_finding: Pathfinding
    fight_turn_behavior: FightTurnBehavior
    fight_preparation_behavior: FightPreparationBehavior
    shared_signals: SharedSignals
    login: str

    def run(self) -> None:
        self.run_timer(FIGHT_TIMEOUT_SECONDS, self.on_fight_timeout)
        self.event_manager.on(
            MapComplementaryInformationEvent,
            callback=self.on_map_complementary_information_event,
            originator=self,
            once=True,
        )
        if not self.game_state.map.is_in_map_transition:
            self.on_fight_map_initialized()
        else:
            self.event_manager.on(
                FightMapInformationEvent,
                lambda _: self.on_fight_map_initialized(),
                originator=self,
                once=True,
            )

    def on_fight_map_initialized(self):
        self.event_manager.on(
            FightTurnStartPlayingEvent,
            self.on_player_turn_event,
            originator=self,
        )
        if self.game_state.fight.is_our_turn:
            self.logger.info("It's already our turn, let's play")
            self.on_player_turn()
        elif len(self.game_state.fight.fight_placement_possible_positions) != 0:
            self.logger.info("It's fight preparation time")
            self.fight_preparation_behavior.start(
                callback=self.on_fight_preparation_behavior_finish, parent=self
            )

    def on_map_complementary_information_event(
        self, msg: MapComplementaryInformationEvent
    ):
        self.finish()

    def on_fight_preparation_behavior_finish(self, error_code: str | None):
        self.raise_if_error(error_code)

    def on_player_turn_event(self, msg: FightTurnStartPlayingEvent) -> None:
        self.on_player_turn()

    def on_player_turn(self):
        if not self._can_start_fight_turn():
            return
        if self.game_state.fight.fight_turn > 100:
            self.logger.error("Bot Might be stuck")
            self.shared_signals.launch_account.emit(self.login)
        self.run_timer(BETWEEN_ACTION_RANGE, self._start_fight_turn_if_still_valid)

    def _start_fight_turn_if_still_valid(self) -> None:
        if not self._can_start_fight_turn():
            return
        self.fight_turn_behavior.start(callback=None, parent=self)

    def _can_start_fight_turn(self) -> bool:
        return (
            self.game_state.fight.in_fight
            and self.fight_turn_behavior.state == BehaviorState.STOPPED
        )

    def on_fight_timeout(self):
        self.logger.error("Fight timeout reached (30 min), relaunching game")
        self.shared_signals.launch_account.emit(self.login)
