import os
from dataclasses import dataclass

from D3Mapping.d3_mapping.resources.protos.game.fight_pb2 import (
    FightTurnStartPlayingEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)
from src.const import RECORDING_FOLDER
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.fight.fight_preparation_behavior import (
    FightPreparationBehavior,
)
from src.core.behaviors.farms.fight.fight_turn_behavior import FightTurnBehavior
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.signals.shared_farm_signals import SharedSignals
from src.services.human_timings import HumanTimingsService
from src.services.recorder import Recorder

FIGHT_TIMEOUT_SECONDS = 30 * 60


@dataclass
class FightBehavior(Behavior):
    path_finding: Pathfinding
    fight_turn_behavior: FightTurnBehavior
    fight_preparation_behavior: FightPreparationBehavior
    recorder: Recorder
    shared_signals: SharedSignals
    login: str

    def run(self):
        self.run_timer(FIGHT_TIMEOUT_SECONDS, self.on_fight_timeout)
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
                once=True,
            )

    def on_fight_map_initialized(self):
        self.event_manager.on(
            FightTurnStartPlayingEvent,
            lambda _: self.on_player_turn(),
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

    def on_player_turn(self):
        if self.game_state.fight.fight_turn > 100:
            self.logger.error("Bot Might be stuck")
            self.recorder.save(
                os.path.join(
                    RECORDING_FOLDER,
                    f"fight_bot_stuck_{self.recorder.session_id}.jsonl",
                )
            )
            self.shared_signals.launch_account.emit(self.login)
        self.run_timer(
            HumanTimingsService().get_timing_before_playing_turn(),
            lambda: self.fight_turn_behavior.start(callback=None, parent=self),
        )

    def on_fight_timeout(self):
        self.logger.error("Fight timeout reached (30 min), relaunching game")
        self.recorder.save(
            os.path.join(
                RECORDING_FOLDER,
                f"fight_timeout_{self.recorder.session_id}.jsonl",
            )
        )
        self.shared_signals.launch_account.emit(self.login)
