from dataclasses import dataclass, field
from datetime import datetime
from threading import Event, Thread
from time import sleep
from typing import Any, Callable

import psutil
import schedule
from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey
from d3_mapping.signals.message_signals import MessageInfoSignals
from models.datas.recipe_root import RecipeItem
from PyQt5.QtCore import QThread

from src.common.logger import Logger
from src.controller.bot_config import BotConfig, BotConfigController
from src.core.behaviors.auto.auto_bot_behavior import AutoBotBehavior
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.dungeons.dungeon_behavior import DungeonBehavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.fight.revive_behavior import ReviveBehavior
from src.core.behaviors.mule_storage.mule_accept_behavior import (
    MuleAcceptBehavior,
)
from src.core.config.mule import (
    MULE_BANK_CHARACTER_LOGIN,
)
from src.core.frames.frame import Frame
from src.core.logic.dungeons.consts import DUNGEONS_INFOS
from src.core.states.game_state import GameState
from src.event_manager import EventManager
from src.exceptions import UnhandledErrorCodeException
from src.gui.utils.run_in_background import Worker, run_in_background
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

    event_manager: EventManager

    game_state: GameState

    grid_signals: GridSignals
    bot_signals: BotSignals
    game_info_signals: GameInfoSignals
    msg_info_signals: MessageInfoSignals
    world_signals: WorldSignals
    log_signals: LogSignals

    frames: list[Frame]

    mule_accept_kamas_behavior: MuleAcceptBehavior
    harvester_behavior: HarvesterBehavior
    fighter_behavior: FighterBehavior
    craft_behavior: CraftBehavior
    fight_behavior: FightBehavior
    auto_bot_behavior: AutoBotBehavior
    revive_behavior: ReviveBehavior
    dungeon_behavior: DungeonBehavior

    usable_behaviors: list[Behavior]

    logger: Logger
    is_connected_event: Event
    is_ready_to_play_event: Event
    is_playing_event: Event
    shared_signals: SharedSignals

    _thread_worker_runnings: list[tuple[QThread, Worker]] = field(
        init=False, default_factory=list
    )
    _current_bot_action_func: Callable[..., Any] | None = field(
        init=False, default=None
    )

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
        self.bot_signals.play_auto_bot.connect(self.on_play_auto_bot)
        self.bot_signals.play_usable_behavior.connect(self.on_play_usable_behavior)

    def on_play_usable_behavior(self, behavior_class_name: str):
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

    def start(self):
        bot_config = (
            BotConfigController()
            .get_bot_config_by_login()
            .get(self.account["apikey"]["login"])
        )

        if self.account["apikey"]["login"] in MULE_BANK_CHARACTER_LOGIN:
            self.bot_signals.play_mule_kamas.emit()
        elif bot_config is not None:
            self.thread_planning = Thread(
                target=self.start_planning_bot, daemon=True, args=(bot_config,)
            )
            self.thread_planning.start()
            now = datetime.now()

            start_hour = int(bot_config.playtime_start.split(":")[0])
            end_hour = int(bot_config.playtime_end.split(":")[0])

            if (
                start_hour > end_hour
                and (now.hour >= start_hour or now.hour < end_hour)
            ) or (
                start_hour < end_hour and now.hour >= start_hour and now.hour < end_hour
            ):
                self.bot_signals.play.emit()
                self.shared_signals.launch_account.emit(self.account["apikey"]["login"])

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
        if not self.is_playing_event.is_set():
            return

        bot_config = (
            BotConfigController()
            .get_bot_config_by_login()
            .get(self.account["apikey"]["login"])
        )
        if self._current_bot_action_func is None and bot_config is None:
            raise ValueError("An action should be provided if is_playing_event is set")

        def on_fight_behavior_finished(error_code: str | None):
            if error_code is not None:
                raise UnhandledErrorCodeException(error_code)
            self.run_current_bot_action()

        def on_live_and_kicking(error_code: str | None):
            for dungeon_info in DUNGEONS_INFOS:
                if (
                    self.game_state.map.map_id in dungeon_info.dungeon.mapIds
                    or self.game_state.map.map_id == dungeon_info.dungeon.exitMapId
                ):
                    return self.dungeon_behavior.start(
                        dungeon_info=dungeon_info,
                        callback=on_live_and_kicking,
                        parent=None,
                    )
            if self.game_state.fight.in_fight:
                self.fight_behavior.start(
                    callback=on_fight_behavior_finished,
                    parent=None,
                )
            else:
                self.run_current_bot_action()

        self.revive_behavior.start(callback=on_live_and_kicking, parent=None)

    def guess_bot_action(self):
        if self.account["apikey"]["login"] in MULE_BANK_CHARACTER_LOGIN:
            self.bot_signals.play_mule_kamas.emit()
        elif (
            BotConfigController()
            .get_bot_config_by_login()
            .get(self.account["apikey"]["login"])
            is not None
        ):
            self.bot_signals.play_auto_bot.emit(None, None)

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
    ):
        self.play_action(
            lambda: self.fighter_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(),
                parent=None,
                area_id=area_id,
                sub_area_id=sub_area_id,
            )
        )

    def on_play_auto_bot(
        self,
        area_id: int | None,
        sub_area_id: int | None,
    ):
        self.play_action(
            lambda: self.auto_bot_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(),
                parent=None,
                area_id=area_id,
                sub_area_id=sub_area_id,
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
        if self.mule_accept_kamas_behavior.is_running.is_set():
            self.mule_accept_kamas_behavior.stop()
        if self.auto_bot_behavior.is_running.is_set():
            self.auto_bot_behavior.stop()
        if self.revive_behavior.is_running.is_set():
            self.revive_behavior.stop()

    def stop_running_behaviors(self):
        if self.harvester_behavior.is_running.is_set():
            self.harvester_behavior.finish()
        if self.fighter_behavior.is_running.is_set():
            self.fighter_behavior.finish()
        if self.craft_behavior.is_running.is_set():
            self.craft_behavior.finish()
        if self.fight_behavior.is_running.is_set():
            self.fight_behavior.stop()
        if self.mule_accept_kamas_behavior.is_running.is_set():
            self.mule_accept_kamas_behavior.finish()
        if self.auto_bot_behavior.is_running.is_set():
            self.auto_bot_behavior.finish()
        if self.revive_behavior.is_running.is_set():
            self.revive_behavior.finish()

    def start_planning_bot(self, bot_config: BotConfig):
        def planned_stop_bot():
            self.logger.info("Stopping bot")
            if self.is_playing_event.is_set():
                self.safe_stop()
                self.bot_signals.stop.emit()
                self.kill_process()
            else:
                self.logger.info("Bot is not playing, dont stop")

        def planned_restart_bot():
            self.logger.info("Restarting bot")
            if not self.is_playing_event.is_set():
                self.bot_signals.play.emit()
                self.shared_signals.launch_account.emit(self.account["apikey"]["login"])
            else:
                self.logger.info("Bot is playing, dont restart")

        schedule.every().day.at(bot_config.playtime_end).do(
            lambda: self._thread_worker_runnings.append(
                run_in_background(planned_stop_bot)
            )
        )
        schedule.every().day.at(bot_config.playtime_start).do(
            lambda: self._thread_worker_runnings.append(
                run_in_background(planned_restart_bot)
            )
        )

    def kill_process(self):
        if self.pid is None:
            return
        try:
            process = psutil.Process(self.pid)
            process.terminate()
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                self.logger.info("timeout, force kill process")
                process.kill()
            self.logger.info(f"killed pid : {self.pid}")
        except psutil.NoSuchProcess:
            self.logger.info("process of related pid is not running anymore, skip.")
        self.pid = None
