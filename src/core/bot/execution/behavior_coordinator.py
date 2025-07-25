from collections.abc import Callable
from dataclasses import dataclass, field, fields
from threading import Event

from ankama_launcher_emulator_premium.gui.utils import run_in_background
from ankama_launcher_emulator_premium.interfaces.credentials import (
    StoredApiKey,
)
from dofus_unity_reader.models.datas.recipe_root import RecipeItem

from src.controller.bot_config import BotConfig, BotConfigService
from src.core.behaviors.behavior import Behavior, BehaviorState
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.auto_bot_behavior import AutoBotBehavior
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.mule_storage.mule_accept_behavior import MuleAcceptBehavior
from src.core.events_manager.event_manager import EventManager
from src.core.signals.bot_signals import BotSignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.states.player_state import PlayerState
from src.services.logging_utils.contextual_logger import ContextualLogger


@dataclass
class BehaviorCoordinator(ContextualLogger):
    """Coordinates and orchestrates bot behaviors execution."""

    is_connected_event: Event
    is_ready_to_play_event: Event
    is_playing_event: Event
    from_manual_play: Event

    event_manager: EventManager

    fight_behavior: FightBehavior
    harvester_behavior: HarvesterBehavior
    fighter_behavior: FighterBehavior
    craft_behavior: CraftBehavior
    mule_accept_kamas_behavior: MuleAcceptBehavior
    auto_bot_behavior: AutoBotBehavior
    usable_behaviors: list[Behavior]

    bot_signals: BotSignals
    shared_signals: SharedSignals
    player_state: PlayerState

    account: StoredApiKey
    get_bot_config: Callable[[], BotConfig | None]

    _current_bot_action_func: Callable[[Callable[[str], None]], None] | None = field(
        init=False, default=None
    )

    def on_play(self, from_manual_play: bool):
        if from_manual_play:
            self.from_manual_play.set()
        else:
            self.from_manual_play.clear()
        self.is_playing_event.set()

    def on_stop(self):
        self.is_playing_event.clear()
        self._current_bot_action_func = None
        run_in_background(lambda _progress_callback: self.stop_behaviors())

    def on_play_usable_behavior(self, behavior_class_name: str):
        """Execute a usable behavior by class name."""
        related_behavior = next(
            behavior
            for behavior in self.usable_behaviors
            if behavior.__class__.__name__ == behavior_class_name
        )
        self.play_action(
            lambda _progress_callback: related_behavior.start(  # type: ignore
                callback=lambda *_args: self.bot_signals.stop.emit(),  # type: ignore
                parent=None,
            )
        )

    def on_play_harvester(self, area_id: int | None, sub_area_id: int | None):
        self.play_action(
            lambda _progress_callback: self.harvester_behavior.start(
                callback=lambda *_args: self.bot_signals.stop.emit(),
                parent=None,
                area_id=area_id,
                sub_area_id=sub_area_id,
            )
        )

    def on_play_mule_kamas(self):
        self.play_action(
            lambda _progress_callback: self.mule_accept_kamas_behavior.start(
                callback=lambda *_args: self.bot_signals.stop.emit(), parent=None
            )
        )

    def on_play_fighter(
        self,
        area_id: int | None,
        sub_area_id: int | None,
    ):
        self.play_action(
            lambda _progress_callback: self.fighter_behavior.start(
                callback=lambda *_args: self.bot_signals.stop.emit(),
                parent=None,
                area_id=area_id,
                sub_area_id=sub_area_id,
            )
        )

    def on_play_auto_bot(self):
        self.play_action(
            lambda _progress_callback: self.auto_bot_behavior.start(
                callback=lambda *_args: self.bot_signals.stop.emit(),
                parent=None,
                area_id=None,
                sub_area_id=None,
            )
        )

    def on_play_crafter(self, recipes: list[RecipeItem]):
        self.play_action(
            lambda _progress_callback: self.craft_behavior.start(
                callback=lambda *_args: self.bot_signals.stop.emit(),
                parent=None,
                recipes=recipes,
            )
        )

    def play_action(self, func: Callable[[Callable[[str], None]], None]) -> None:
        """Setup and execute a bot action."""
        self.stop_behaviors()
        self._current_bot_action_func = func
        if not self.is_connected_event.is_set():
            self.shared_signals.launch_account.emit(self.account.apikey.login)
        elif self.is_ready_to_play_event.is_set():
            run_in_background(self._current_bot_action_func)
        else:
            self.logger.info("character is probably connecting, waiting...")

    def run_current_bot_action(self) -> None:
        """Execute the current bot action or guess the appropriate one."""
        if self._current_bot_action_func is not None:
            run_in_background(self._current_bot_action_func)
        else:
            self.guess_bot_action()

    def guess_bot_action(self) -> None:
        """Determine and trigger the appropriate bot action based on configuration."""
        is_kamas_mule = BotConfigService().is_kamas_mule(
            self.account.apikey.login
        )
        if (
            is_kamas_mule
            and self.player_state.level >= 50
            and self.player_state.is_former_sub
        ):
            self.bot_signals.play_mule_kamas.emit()
            return
        config = self.get_bot_config()
        if config is not None and config.schedule_profile is not None:
            self.bot_signals.play_auto_bot.emit()

    def stop_behaviors(self) -> None:
        with self.event_manager.lock:
            for behavior in self.running_top_level_behaviors():
                behavior.stop()

    def running_top_level_behaviors(self) -> list[Behavior]:
        """Top-level (parent-less) action behaviors currently RUNNING."""
        running: list[Behavior] = []
        for field_info in fields(self):
            field_value = getattr(self, field_info.name)
            if (
                isinstance(field_value, Behavior)
                and field_value.state == BehaviorState.RUNNING
            ):
                running.append(field_value)

        for usable_behavior in self.usable_behaviors:
            if usable_behavior.state == BehaviorState.RUNNING:
                running.append(usable_behavior)
        return running
