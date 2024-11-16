from dataclasses import dataclass, field
from threading import Event, Timer

from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.controller.bot_config import BotConfig
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.quests.dungeon_behavior import DungeonBehavior
from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator
from src.core.engine.movements.world.edge import (
    remove_forbidden_edge_transition_by_map_id,
)
from src.core.game_constants import DUNGEONS_INFOS
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.states.game_state import GameState
from src.exceptions import UnhandledErrorCodeException
from src.services.logging.logger import Logger


@dataclass
class ConnectionHandler:
    """Handles bot connection/disconnection lifecycle events."""

    is_connected_event: Event
    is_ready_to_play_event: Event
    is_playing_event: Event
    game_state: GameState
    dungeon_behavior: DungeonBehavior
    fight_behavior: FightBehavior
    logger: Logger
    account: DecipheredApiKey
    shared_signals: SharedSignals
    bot_config: BotConfig | None

    behavior_coordinator: BehaviorCoordinator

    _timer_disconnected: Timer | None = field(init=False, default=None)

    def on_connected(self):
        self.is_connected_event.set()

    def on_disconnected(self):
        """Handle bot disconnection event and trigger reconnection if playing."""
        self.is_connected_event.clear()
        self.is_ready_to_play_event.clear()
        if not self.is_playing_event.is_set():
            return
        self.logger.info("disconnected, relaunch bot")
        if self.behavior_coordinator:
            self.behavior_coordinator.stop_behaviors()
        self._timer = Timer(
            3,
            lambda: self.shared_signals.launch_account.emit(
                self.account["apikey"]["login"]
            ),
        )
        self._timer.start()

    def on_ready_to_play(self):
        """Handle ready to play event and start appropriate behavior."""
        self.is_ready_to_play_event.set()
        if not self.is_playing_event.is_set():
            return

        if not self.behavior_coordinator or (
            self.behavior_coordinator._current_bot_action_func is None
            and self.bot_config is None
        ):
            raise ValueError("An action should be provided if is_playing_event is set")

        remove_forbidden_edge_transition_by_map_id(self.game_state.map.map_id)

        def on_fight_behavior_finished(error_code: str | None):
            if error_code is not None:
                raise UnhandledErrorCodeException(error_code)
            if self.behavior_coordinator:
                self.behavior_coordinator.run_current_bot_action()

        def on_dungeon_behavior_finished(error_code: str | None):
            if error_code is not None:
                raise UnhandledErrorCodeException(error_code)
            if self.behavior_coordinator:
                self.behavior_coordinator.run_current_bot_action()

        for dungeon_info in DUNGEONS_INFOS:
            if (
                self.game_state.map.map_id in dungeon_info.dungeon.mapIds
                or self.game_state.map.map_id == dungeon_info.dungeon.exitMapId
            ):
                return self.dungeon_behavior.start(
                    dungeon_info=dungeon_info,
                    callback=on_dungeon_behavior_finished,
                    parent=None,
                )

        if self.game_state.fight.in_fight:
            self.fight_behavior.start(
                callback=on_fight_behavior_finished,
                parent=None,
            )
        else:
            if self.behavior_coordinator:
                self.behavior_coordinator.run_current_bot_action()
