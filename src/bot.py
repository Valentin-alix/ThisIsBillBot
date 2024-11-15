import base64
import time
from dataclasses import dataclass, field, fields
from datetime import datetime
from functools import cached_property
from threading import Event, Thread, Timer
from time import sleep
from typing import Any, Callable

import psutil
import schedule
from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey
from d3_mapping.models.message import MessageInfo
from d3_mapping.protocol.protocol_game import POOL
from d3_mapping.signals.message_signals import MessageInfoSignals
from google.protobuf.descriptor import Descriptor
from google.protobuf.json_format import MessageToDict
from google.protobuf.message_factory import GetMessageClass
from models.datas.recipe_root import RecipeItem
from PyQt5.QtCore import QThread

from src.common.dataclass_utils import apply_dict_to_dataclass
from src.common.internet import has_internet_connection
from src.common.logger import Logger
from src.common.timing import is_in_playtime
from src.controller.bot_config import BotConfig, BotConfigController
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.auto_bot_behavior import AutoBotBehavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.fight.revive_behavior import ReviveBehavior
from src.core.behaviors.mule_storage.mule_accept_behavior import MuleAcceptBehavior
from src.core.behaviors.quests.dungeon_behavior import DungeonBehavior
from src.core.config.mule import MULE_BANK_CHARACTER_LOGIN
from src.core.frames.frame import Frame
from src.core.logic.dungeons.consts import DUNGEONS_INFOS
from src.core.logic.world.edge import remove_forbidden_edge_transition_by_map_id
from src.core.states.game_state import GameState
from src.event_manager import EventManager
from src.exceptions import UnhandledErrorCodeException
from src.gui.utils.run_in_background import Worker, run_in_background
from src.signals.bot_signals import BotSignals
from src.signals.grid_signals import GridSignals
from src.signals.log_signals import LogSignals
from src.signals.player_signals import GameInfoSignals, InventorySignals
from src.signals.replay_signals import ReplaySignals
from src.signals.shared_farm_signals import SharedSignals
from src.signals.world_signals import WorldSignals
from src.tools.recorder import Recorder


@dataclass
class Bot:
    pid: int | None
    account: DecipheredApiKey

    event_manager: EventManager

    game_state: GameState

    is_fake: bool

    recorder: Recorder

    replay_signals: ReplaySignals
    grid_signals: GridSignals
    bot_signals: BotSignals
    inventory_signals: InventorySignals
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
    from_manual_play: Event = field(init=False, default_factory=Event)

    _timer_disconnected: Timer | None = field(init=False, default=None)
    _thread_worker_runnings: list[tuple[QThread, Worker]] = field(
        init=False, default_factory=list
    )
    _current_bot_action_func: Callable[..., Any] | None = field(
        init=False, default=None
    )

    @cached_property
    def bot_config(self):
        return (
            BotConfigController()
            .get_bot_config_by_login()
            .get(self.account["apikey"]["login"])
        )

    def __str__(self):
        return self.account["apikey"]["login"]

    def __repr__(self):
        return self.__str__()

    def __post_init__(self):
        self.game_info_signals.connected.connect(self.on_connected)
        self.game_info_signals.disconnected.connect(self.on_disconnected)
        self.replay_signals.replay_requested.connect(self.replay)
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
        bot_config = self.bot_config

        if bot_config is not None:
            self.thread_planning = Thread(
                target=self.start_planning_bot, daemon=True, args=(bot_config,)
            )
            self.thread_planning.start()
            now = datetime.now()

            if is_in_playtime(
                now, bot_config.playtime_starts, bot_config.playtime_ends
            ):
                self.bot_signals.play.emit(False)
                self.shared_signals.launch_account.emit(self.account["apikey"]["login"])

    def on_connected(self):
        self.is_connected_event.set()

    def on_disconnected(self):
        self.is_connected_event.clear()
        self.is_ready_to_play_event.clear()
        if not self.is_playing_event.is_set():
            return
        self.logger.info("disconnected, relaunch bot")
        self.stop_behaviors()
        self._timer = Timer(
            3,
            lambda: self.shared_signals.launch_account.emit(
                self.account["apikey"]["login"]
            ),
        )
        self._timer.start()

    def on_play(self, from_manual_play: bool):
        if from_manual_play:
            self.from_manual_play.set()
        else:
            self.from_manual_play.clear()
        self.is_playing_event.set()

    def on_stop(self):
        self.logger.info("stopping")
        self.is_playing_event.clear()
        self._current_bot_action_func = None
        self.stop_behaviors()

    def on_ready_to_play(self):
        self.is_ready_to_play_event.set()
        if not self.is_playing_event.is_set():
            return

        bot_config = self.bot_config
        if self._current_bot_action_func is None and bot_config is None:
            raise ValueError("An action should be provided if is_playing_event is set")

        remove_forbidden_edge_transition_by_map_id(self.game_state.map.map_id)

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

        self._thread_worker_runnings.append(
            run_in_background(
                lambda: self.revive_behavior.start(
                    callback=on_live_and_kicking, parent=None
                )
            )
        )

    def guess_bot_action(self):
        if self.account["apikey"]["login"] in MULE_BANK_CHARACTER_LOGIN:
            self.bot_signals.play_mule_kamas.emit()
        elif self.bot_config is not None:
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
        self.stop_behaviors()
        self._current_bot_action_func = func
        if not self.is_connected_event.is_set():
            self.logger.info("relaunching from play action")
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
        self.stop_behaviors()

    def stop_behaviors(self):
        for field_info in fields(self):
            field_value = getattr(self, field_info.name)
            if isinstance(field_value, Behavior) and field_value.is_running.is_set():
                field_value.stop()

        for usable_behavior in self.usable_behaviors:
            if usable_behavior.is_running.is_set():
                usable_behavior.stop()

    def start_planning_bot(self, bot_config: BotConfig):
        def planned_stop_bot():
            self.logger.info("Stopping bot")
            self.log_signals.clear_logs.emit()
            self.msg_info_signals.clear_msg_infos.emit()
            if self.is_playing_event.is_set():
                self.safe_stop()
                self.bot_signals.stop.emit()
                self.kill_process()
            else:
                self.logger.info("Bot is not playing, dont stop")

        def planned_restart_bot():
            self.logger.info("Restarting bot")
            now = datetime.now()
            while not has_internet_connection():
                self.logger.info(
                    "waiting for internet connection to be up in restart bot"
                )
                sleep(1)
            if bot_config and not is_in_playtime(
                now, bot_config.playtime_starts, bot_config.playtime_ends
            ):
                return self.logger.info("Bot is not anymore in playtime")

            if not self.is_playing_event.is_set():
                self.bot_signals.play.emit(False)
                self.logger.info("relaunching from planning")
                self.shared_signals.launch_account.emit(self.account["apikey"]["login"])
            else:
                self.logger.info("Bot is playing, dont restart")

        for playtime_end in bot_config.playtime_ends:
            schedule.every().day.at(playtime_end).do(
                lambda: self._thread_worker_runnings.append(
                    run_in_background(planned_stop_bot)
                )
            )

        for playtime_start in bot_config.playtime_starts:
            schedule.every().day.at(playtime_start).do(
                lambda: self._thread_worker_runnings.append(
                    run_in_background(planned_restart_bot)
                )
            )

    def kill_process(self):
        if self.pid is None:
            return self.logger.warning("No pid to kill")
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

    def replay(
        self, path: str, preserve_timing: bool = False, speedup: float | None = None
    ) -> None:
        def _worker():
            did_apply_state: bool = False
            last_timestamp: float | None = None
            for record_line in self.recorder.load(path):
                if record_line.get("type") == "state":
                    apply_dict_to_dataclass(self.game_state, record_line["state"])
                    did_apply_state = True
                    continue
                if record_line.get("type") != "message":
                    continue
                if not did_apply_state:
                    continue
                curr_timestamp = time.mktime(
                    datetime.fromisoformat(
                        record_line["timestamp"].replace("Z", "")
                    ).timetuple()
                )
                if preserve_timing and last_timestamp is not None:
                    wait = curr_timestamp - last_timestamp
                    if speedup:
                        wait = wait / speedup
                    if wait > 0:
                        time.sleep(wait)
                last_timestamp = curr_timestamp
                payload = base64.b64decode(record_line.get("payload_b64", ""))
                full_name = record_line["msg_full_name"]
                msg_descriptor: Descriptor = POOL.FindMessageTypeByName(full_name)
                msg_type = GetMessageClass(msg_descriptor)
                msg = msg_type()
                msg.ParseFromString(payload)

                msg_info = MessageInfo(
                    received_time=datetime.fromtimestamp(curr_timestamp),
                    from_server=record_line["from_server"],
                    msg_json=MessageToDict(msg),
                    sub_msg_name=msg.__class__.__name__,
                    obf_msg_json=None,
                )
                self.msg_info_signals.msg_info.emit(msg_info, False)
                self.event_manager.process_msg(msg)

        self._thread_worker_runnings.append(run_in_background(_worker))
