from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Event, Timer

from ankama_launcher_emulator_premium.interfaces.credentials import (
    StoredApiKey,
)
from datas.protos.non_obf.game.common_pb2 import Character
from dofus_unity_reader.data_center.dungeon_info import PLAYABLE_DUNGEONS
from dofus_unity_reader.game_constants.map_id import MapIdEnum

from src.controller.bot_config import BotConfig
from src.core.behaviors.account.character_creation_behavior import (
    CharacterCreationBehavior,
)
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.quests.dungeon_behavior import DungeonBehavior
from src.core.behaviors.quests.tutorial_behavior import TutorialBehavior
from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator
from src.core.engine.movements.world.edge import (
    remove_forbidden_edge_transition_by_map_id,
)
from src.core.events_manager.event_manager import (
    EventManager,
)
from src.core.signals.bot_signals import BotSignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.states.game_state import GameState
from src.exceptions import UnhandledErrorCodeException
from src.services.logging_utils.contextual_logger import ContextualLogger


@dataclass
class ConnectionHandler(ContextualLogger):
    """Handles bot connection/disconnection lifecycle events."""

    is_connected_event: Event
    bot_signals: BotSignals
    is_ready_to_play_event: Event
    is_playing_event: Event
    game_state: GameState
    dungeon_behavior: DungeonBehavior
    fight_behavior: FightBehavior
    character_creation_behavior: CharacterCreationBehavior
    tutorial_behavior: TutorialBehavior
    account: StoredApiKey
    shared_signals: SharedSignals
    get_bot_config: Callable[[], BotConfig | None]
    event_manager: EventManager

    behavior_coordinator: BehaviorCoordinator

    _timer: Timer | None = field(init=False, default=None)
    _reconnect_attempts: int = field(init=False, default=0)

    def cleanup(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def on_connected(self, characters: list[Character]) -> None:
        self.is_connected_event.set()
        if (
            not self.event_manager.is_socket_mode
            and len(characters) == 0
            and self.is_playing_event.is_set()
        ):
            self.character_creation_behavior.start(
                callback=self.on_character_creation_behavior_finished, parent=None
            )

    def on_character_creation_behavior_finished(self, error_code: str | None) -> None:
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

    def on_disconnected(self) -> None:
        """Handle bot disconnection event and trigger reconnection if playing."""
        self.is_connected_event.clear()
        self.is_ready_to_play_event.clear()
        self.game_state.clear_connection_scoped_state()
        if not self.is_playing_event.is_set():
            self._reconnect_attempts = 0
            return

        self.logger.info(
            f"Bot unexpected disconnect, reconnect attemp : {self._reconnect_attempts}"
        )

        self._reconnect_attempts += 1

        if self._reconnect_attempts > 3:
            self.logger.warning("Max reconnected attempt reached, stopping bot.")
            self.bot_signals.stop.emit()
            self._reconnect_attempts = 0
            return

        self.behavior_coordinator.stop_behaviors()
        self.cleanup()

        delay = 10 + (self._reconnect_attempts * 10)
        self._timer = Timer(delay, self._emit_relaunch)
        self._timer.start()

    def _emit_relaunch(self):
        self.logger.info("Relaunching bot")
        if self.is_playing_event.is_set():
            self.shared_signals.launch_account.emit(self.account.apikey.login)

    def on_ready_to_play(self):
        """Handle ready to play event and start appropriate behavior."""
        self.is_ready_to_play_event.set()
        self._reconnect_attempts = 0
        if not self.is_playing_event.is_set():
            return

        if (
            self.behavior_coordinator._current_bot_action_func is None
            and self.get_bot_config() is None
        ):
            raise ValueError("An action should be provided if is_playing_event is set")

        remove_forbidden_edge_transition_by_map_id(
            self.game_state.map.map_id,
            self.game_state.map.forbidden_edge_transitions,
        )

        def on_fight_behavior_finished(error_code: str | None):
            if error_code is not None:
                raise UnhandledErrorCodeException(error_code)
            if (
                self.behavior_coordinator
                and self.behavior_coordinator.is_playing_event.is_set()
            ):
                self.behavior_coordinator.run_current_bot_action()

        def on_dungeon_behavior_finished(error_code: str | None):
            if error_code is not None:
                raise UnhandledErrorCodeException(error_code)
            if (
                self.behavior_coordinator
                and self.behavior_coordinator.is_playing_event.is_set()
            ):
                self.behavior_coordinator.run_current_bot_action()

        def on_tutorial_behavior_finished(error_code: str | None):
            if error_code is not None:
                raise UnhandledErrorCodeException(error_code)
            if (
                self.behavior_coordinator
                and self.behavior_coordinator.is_playing_event.is_set()
            ):
                self.behavior_coordinator.run_current_bot_action()

        if self.game_state.map.map_id == MapIdEnum.TUTORIAL_STARTING_MAP:
            return self.tutorial_behavior.start(
                callback=on_tutorial_behavior_finished, parent=None
            )

        for dungeon_info in PLAYABLE_DUNGEONS:
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
        elif self.behavior_coordinator.is_playing_event.is_set():
            self.behavior_coordinator.run_current_bot_action()
