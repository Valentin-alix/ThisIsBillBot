from dataclasses import dataclass
from threading import Event
from time import sleep

from PyQt5.QtCore import QThread
from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from models.datas.recipe_root import RecipeItem
from src.common.logger import Logger
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.fighter.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.fighter.mule_fighter_behavior import MuleFighterBehavior
from src.core.behaviors.farms.harvest.harvester_behavior import HarvesterBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.frames.frame import Frame
from src.core.states.game_state import GameState
from src.event_manager import EventManager
from src.gui.utils.run_in_background import run_in_background, Worker
from src.signals.bot_signals import BotSignals
from src.signals.grid_signals import GridSignals
from src.signals.log_signals import LogSignals
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import WorldSignals


@dataclass
class Bot:
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
    harvester_behavior: HarvesterBehavior
    fighter_behavior: FighterBehavior
    craft_behavior: CraftBehavior
    mule_fighter_behavior: MuleFighterBehavior
    fight_behavior: FightBehavior
    logger: Logger
    is_playing_event: Event

    _thread_worker_running: tuple[QThread, Worker] | None = None

    def __str__(self):
        return self.game_state.player.character_name

    def __repr__(self):
        return self.__str__()

    def __post_init__(self):
        self.bot_signals.play_harvester.connect(self.on_play_harvester)
        self.bot_signals.play_craft.connect(self.on_play_craft)
        self.bot_signals.stop.connect(self.stop_main_behavior)
        self.game_info_signals.disconnected.connect(self.stop_main_behavior)
        self.bot_signals.play.connect(self.on_play)
        self.bot_signals.stop.connect(self.on_stop)

    def on_play(self):
        self.is_playing_event.set()

    def on_stop(self):
        self.is_playing_event.clear()

    def on_play_harvester(self, area_id: int | None, sub_area_id: int | None):
        self.stop_main_behavior()
        self.bot_signals.play.emit()
        self._thread_worker_running = run_in_background(
            lambda: self.harvester_behavior.start(
                callback=lambda _: self.bot_signals.stop.emit(),
                parent=None,
                area_id=area_id,
                sub_area_id=sub_area_id,
            )
        )

    def on_play_craft(self, recipes: list[RecipeItem]):
        self.stop_main_behavior()
        self.bot_signals.play.emit()
        self.craft_behavior.start(
            recipes=recipes,
            parent=None,
            callback=lambda _: self.bot_signals.stop.emit(),
        )

    def safe_stop(self):
        while self.fight_behavior.is_running.is_set():
            sleep(0.3)
        self.stop_main_behavior()

    def stop_main_behavior(self):
        if self.harvester_behavior.is_running.is_set():
            self.harvester_behavior.finish()
        if self.fighter_behavior.is_running.is_set():
            self.fighter_behavior.finish()
        if self.mule_fighter_behavior.is_running.is_set():
            self.mule_fighter_behavior.finish()
        if self.craft_behavior.is_running.is_set():
            self.craft_behavior.finish()
