from dataclasses import dataclass, field, fields
from threading import Event
from typing import Any, Callable

from ankama_launcher_emulator_premium.gui.utils import run_in_background
from ankama_launcher_emulator_premium.interfaces.deciphered_api_key import (
    DecipheredApiKey,
)
from d3_database.models.datas.recipe_root import RecipeItem
from PyQt6.QtCore import QThread

from src.controller.bot_config import BotConfig
from src.core.behaviors.behavior import Behavior, BehaviorState
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.auto_bot_behavior import AutoBotBehavior
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.mule_storage.mule_accept_behavior import MuleAcceptBehavior
from src.core.config import MULE_BANK_CHARACTER_LOGIN
from src.core.events_manager.event_manager import EventManager
from src.core.signals.bot_signals import BotSignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.services.logging.contextual_logger import ContextualLogger


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

    account: DecipheredApiKey
    get_bot_config: Callable[[], BotConfig | None]

    _thread_worker_runnings: list[tuple[QThread, Any]] = field(
        init=False, default_factory=list
    )
    _current_bot_action_func: Callable[..., Any] | None = field(
        init=False, default=None
    )

    def on_play(self, from_manual_play: bool):
        if from_manual_play:
            self.from_manual_play.set()
        else:
            self.from_manual_play.clear()
        self.is_playing_event.set()

    def on_stop(self):
        self.logger.info("Full Stop")
        self.is_playing_event.clear()
        self._current_bot_action_func = None
        self.stop_behaviors()

    def on_play_usable_behavior(self, behavior_class_name: str):
        """Execute a usable behavior by class name."""
        related_behavior = next(
            behavior
            for behavior in self.usable_behaviors
            if behavior.__class__.__name__ == behavior_class_name
        )
        self.play_action(
            lambda: related_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(), parent=None
            )
        )

    def on_play_harvester(self, area_id: int | None, sub_area_id: int | None):
        self.play_action(
            lambda: self.harvester_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(),
                parent=None,
                area_id=area_id,
                sub_area_id=sub_area_id,
            )
        )

    def on_play_mule_kamas(self):
        self.play_action(
            lambda: self.mule_accept_kamas_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(), parent=None
            )
        )

    def on_play_fighter(
        self,
        area_id: int | None,
        sub_area_id: int | None,
    ):
        self.play_action(
            lambda: self.fighter_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(),
                parent=None,
                area_id=area_id,
                sub_area_id=sub_area_id,
            )
        )

    def on_play_auto_bot(self):
        self.play_action(
            lambda: self.auto_bot_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(),
                parent=None,
                area_id=None,
                sub_area_id=None,
            )
        )

    def on_play_crafter(self, recipes: list[RecipeItem]):
        self.play_action(
            lambda: self.craft_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(),
                parent=None,
                recipes=recipes,
            )
        )

    def play_action(self, func: Callable[[], None]):
        """Setup and execute a bot action."""
        self.stop_behaviors()
        self._current_bot_action_func = func
        if not self.is_connected_event.is_set():
            self.shared_signals.launch_account.emit(self.account["apikey"]["login"])
        elif self.is_ready_to_play_event.is_set():
            run_in_background(self._current_bot_action_func)
        else:
            self.logger.info("character is probably connecting, waiting...")

    def run_current_bot_action(self):
        """Execute the current bot action or guess the appropriate one."""
        if self._current_bot_action_func is not None:
            run_in_background(self._current_bot_action_func)
        else:
            self.guess_bot_action()

    def guess_bot_action(self):
        """Determine and trigger the appropriate bot action based on configuration."""
        if self.account["apikey"]["login"] in MULE_BANK_CHARACTER_LOGIN:
            self.bot_signals.play_mule_kamas.emit()
        elif self.get_bot_config() is not None:
            self.bot_signals.play_auto_bot.emit()

    def stop_behaviors(self):
        with self.event_manager.lock:
            for field_info in fields(self):
                field_value = getattr(self, field_info.name)
                if (
                    isinstance(field_value, Behavior)
                    and field_value.state == BehaviorState.RUNNING
                ):
                    field_value.stop()

            for usable_behavior in self.usable_behaviors:
                if usable_behavior.state == BehaviorState.RUNNING:
                    usable_behavior.stop()
