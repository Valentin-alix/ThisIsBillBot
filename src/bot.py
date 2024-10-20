from dataclasses import dataclass, field
from threading import Event
from time import sleep
from typing import Any, Callable

from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey
from d3_mapping.signals.message_signals import MessageInfoSignals
from models.datas.recipe_root import RecipeItem
from PyQt5.QtCore import QThread

from src.common.logger import Logger
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.fighter.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvest.harvester_behavior import HarvesterBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.mule_kamas.mule_accept_kamas_behavior import (
    MuleAcceptKamasBehavior,
)
from src.core.config.suicide_bots import (
    INCARNAM_BOT_LOGINS,
    MULE_BANK_CHARACTER_ID,
    SUICIDE_BOT_FIGHT_LEVEL_LIMIT,
    NOT_SUICIDE_BOT_LOGINS,
)
from src.core.frames.frame import Frame
from src.core.states.game_state import GameState
from src.event_manager import EventManager
from src.exceptions import UnhandledErrorCodeException
from src.gui.utils.run_in_background import Worker, run_in_background
from src.interfaces.enums.area_enum import AreaEnum
from src.signals.bot_signals import BotSignals
from src.signals.grid_signals import GridSignals
from src.signals.log_signals import LogSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.shared_farm_signals import SharedSignals
from src.signals.world_signals import WorldSignals


@dataclass
class Bot:
    pid: int | None
    account: DecipheredApiKey
    # event manager
    event_manager: EventManager
    # states
    game_state: GameState
    # signals
    grid_signals: GridSignals
    bot_signals: BotSignals
    game_info_signals: GameInfoSignals
    msg_info_signals: MessageInfoSignals
    world_signals: WorldSignals
    log_signals: LogSignals
    # frames
    frames: list[Frame]
    # behaviors
    mule_accept_kamas_behavior: MuleAcceptKamasBehavior
    harvester_behavior: HarvesterBehavior
    fighter_behavior: FighterBehavior
    craft_behavior: CraftBehavior
    fight_behavior: FightBehavior
    logger: Logger
    is_connected_event: Event
    is_ready_to_play_event: Event
    is_playing_event: Event
    shared_signals: SharedSignals

    _thread_worker_runnings: list[tuple[QThread, Worker]] = field(
        init=False, default_factory=list
    )
    _current_bot_action_func: Callable[..., Any] | None = None

    def __str__(self):
        return self.account["apikey"]["login"]

    def __repr__(self):
        return self.__str__()

    def __post_init__(self):
        self.game_info_signals.connected.connect(self.on_connected)
        self.game_info_signals.disconnected.connect(self.on_disconnected)
        self.bot_signals.play.connect(self.on_play)
        self.bot_signals.stop.connect(self.on_stop)
        self.game_info_signals.is_ready_to_play.connect(self.on_ready_to_play)
        self.bot_signals.play_harvester.connect(self.on_play_harvester)
        self.bot_signals.play_fighter.connect(self.on_play_fighter)
        self.bot_signals.play_crafter.connect(self.on_play_crafter)
        self.bot_signals.play_mule_kamas.connect(self.on_play_mule_kamas)

    def on_connected(self):
        self.is_connected_event.set()

    def on_disconnected(self):
        self.is_connected_event.clear()
        self.is_ready_to_play_event.clear()
        if not self.is_playing_event.is_set():
            return
        self.logger.info("disconnected, relaunch bot")
        self.stop_internal_main_behavior()
        self.shared_signals.launch_account.emit(self.account["apikey"]["login"])

    def on_play(self):
        self.is_playing_event.set()

    def on_stop(self):
        self.logger.info("stopping")
        self.is_playing_event.clear()
        self._current_bot_action_func = None
        self.stop_running_behaviors()

    def on_ready_to_play(self):
        self.is_ready_to_play_event.set()
        if (
            self._current_bot_action_func is None
            and self.account["apikey"]["login"] in NOT_SUICIDE_BOT_LOGINS
        ):
            return

        self.bot_signals.play.emit()

        def on_fight_behavior_finished(error_code: str | None):
            if error_code is not None:
                raise UnhandledErrorCodeException(error_code)
            self.run_current_bot_action()

        if self.game_state.fight.in_fight:
            self.fight_behavior.start(
                callback=on_fight_behavior_finished,
                parent=None,
            )
        else:
            self.run_current_bot_action()

    def guess_bot_action(self):
        if self.account["apikey"]["login"] in NOT_SUICIDE_BOT_LOGINS:
            return
        if self.game_state.player.character_id == MULE_BANK_CHARACTER_ID:
            self.bot_signals.play_mule_kamas.emit()
        elif self.game_state.player.level < SUICIDE_BOT_FIGHT_LEVEL_LIMIT:
            self.bot_signals.play_fighter.emit(
                AreaEnum.INCARNAM,
                None,
                (
                    SUICIDE_BOT_FIGHT_LEVEL_LIMIT,
                    lambda: self.bot_signals.play_harvester.emit(AreaEnum.ASTRUB, None),
                ),
            )
        else:
            if self.account["apikey"]["login"] in INCARNAM_BOT_LOGINS:
                self.bot_signals.play_harvester.emit(AreaEnum.INCARNAM, None)
            else:
                self.bot_signals.play_harvester.emit(AreaEnum.ASTRUB, None)

    def run_current_bot_action(self):
        if self._current_bot_action_func is not None:
            self._thread_worker_runnings.append(
                run_in_background(self._current_bot_action_func)
            )
        else:
            self.guess_bot_action()

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
        level_limit_with_callback: tuple[int, Callable[[], None]] | None,
    ):
        self.play_action(
            lambda: self.fighter_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(),
                parent=None,
                area_id=area_id,
                sub_area_id=sub_area_id,
                level_limit_with_callback=level_limit_with_callback,
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
        self.stop_running_behaviors()
        self.bot_signals.play.emit()
        self._current_bot_action_func = func
        if not self.is_connected_event.is_set():
            self.shared_signals.launch_account.emit(self.account["apikey"]["login"])
        elif self.is_ready_to_play_event.is_set():
            self._thread_worker_runnings.append(
                run_in_background(self._current_bot_action_func)
            )
        else:
            self.logger.info("character is probably connecting, waiting...")

    def safe_stop(self):
        while self.fight_behavior.is_running.is_set():
            sleep(0.3)
        self.stop_running_behaviors()

    def stop_internal_main_behavior(self):
        if self.harvester_behavior.is_running.is_set():
            self.harvester_behavior.stop()
        if self.fighter_behavior.is_running.is_set():
            self.fighter_behavior.stop()
        if self.craft_behavior.is_running.is_set():
            self.craft_behavior.stop()
        if self.fight_behavior.is_running.is_set():
            self.fight_behavior.stop()

    def stop_running_behaviors(self):
        if self.harvester_behavior.is_running.is_set():
            self.harvester_behavior.finish()
        if self.fighter_behavior.is_running.is_set():
            self.fighter_behavior.finish()
        if self.craft_behavior.is_running.is_set():
            self.craft_behavior.finish()
        if self.fight_behavior.is_running.is_set():
            self.fight_behavior.stop()
