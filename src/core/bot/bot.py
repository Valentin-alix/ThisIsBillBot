import datetime
from dataclasses import dataclass, field
from threading import Event

from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.controller.bot_config import BotConfigController
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.auto_bot_behavior import AutoBotBehavior
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.mule_storage.mule_accept_behavior import MuleAcceptBehavior
from src.core.behaviors.quests.dungeon_behavior import DungeonBehavior
from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator
from src.core.bot.execution.process_manager import ProcessManager
from src.core.bot.lifecycle.connection_handler import ConnectionHandler
from src.core.bot.lifecycle.scheduler import BotScheduler
from src.core.bot.replay.replay_handler import ReplayHandler
from src.core.events_manager.event_manager import EventManager
from src.core.frames.frame import Frame
from src.core.signals.bot_signals import BotSignals
from src.core.signals.grid_signals import GridSignals
from src.core.signals.log_signals import LogSignals
from src.core.signals.message_signals import MessageInfoSignals
from src.core.signals.player_signals import GameInfoSignals, InventorySignals
from src.core.signals.replay_signals import ReplaySignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.signals.world_signals import WorldSignals
from src.core.states.game_state import GameState
from src.services.logging.contextual_logger import ContextualLogger
from src.services.recorder import Recorder
from src.services.replayer import Replayer


@dataclass
class Bot(ContextualLogger):
    """
    Main bot class representing a single Dofus bot instance.

    This class holds the bot state and delegates responsibilities to specialized handlers:
    - ConnectionHandler: manages connection lifecycle
    - BehaviorCoordinator: orchestrates behavior execution
    - ProcessManager: manages process lifecycle
    - BotScheduler: manages scheduling and playtime
    - ReplayHandler: handles replay functionality
    """

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
    dungeon_behavior: DungeonBehavior

    usable_behaviors: list[Behavior]

    replayer: Replayer
    is_connected_event: Event
    is_ready_to_play_event: Event
    is_playing_event: Event
    shared_signals: SharedSignals
    from_manual_play: Event = field(init=False, default_factory=Event)

    connection_handler: ConnectionHandler = field(init=False)
    behavior_coordinator: BehaviorCoordinator = field(init=False)
    process_manager: ProcessManager = field(init=False)
    scheduler: BotScheduler = field(init=False)
    replay_handler: ReplayHandler = field(init=False)

    def get_bot_config(self):
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
        self.behavior_coordinator = BehaviorCoordinator(
            is_ready_to_play_event=self.is_ready_to_play_event,
            is_playing_event=self.is_playing_event,
            fight_behavior=self.fight_behavior,
            _logger=self.logger,
            account=self.account,
            shared_signals=self.shared_signals,
            event_manager=self.event_manager,
            get_bot_config=self.get_bot_config,
            is_connected_event=self.is_connected_event,
            from_manual_play=self.from_manual_play,
            harvester_behavior=self.harvester_behavior,
            fighter_behavior=self.fighter_behavior,
            craft_behavior=self.craft_behavior,
            auto_bot_behavior=self.auto_bot_behavior,
            mule_accept_kamas_behavior=self.mule_accept_kamas_behavior,
            usable_behaviors=self.usable_behaviors,
            bot_signals=self.bot_signals,
        )
        self.connection_handler = ConnectionHandler(
            is_ready_to_play_event=self.is_ready_to_play_event,
            is_playing_event=self.is_playing_event,
            game_state=self.game_state,
            dungeon_behavior=self.dungeon_behavior,
            fight_behavior=self.fight_behavior,
            _logger=self.logger,
            account=self.account,
            shared_signals=self.shared_signals,
            get_bot_config=self.get_bot_config,
            behavior_coordinator=self.behavior_coordinator,
            is_connected_event=self.is_connected_event,
        )

        self.process_manager = ProcessManager(_logger=self.logger)
        self.scheduler = BotScheduler(
            is_playing_event=self.is_playing_event,
            _logger=self.logger,
            account=self.account,
            shared_signals=self.shared_signals,
            get_bot_config=self.get_bot_config,
            behavior_coordinator=self.behavior_coordinator,
            bot_signals=self.bot_signals,
            log_signals=self.log_signals,
            msg_info_signals=self.msg_info_signals,
            process_manager=self.process_manager,
        )
        self.replay_handler = ReplayHandler(replayer=self.replayer)

        self.game_info_signals.connected.connect(self.connection_handler.on_connected)
        self.game_info_signals.disconnected.connect(
            self.connection_handler.on_disconnected
        )
        self.replay_signals.replay_requested.connect(
            self.replay_handler.on_replay_requested
        )
        self.bot_signals.play.connect(self.behavior_coordinator.on_play)
        self.bot_signals.stop.connect(self.behavior_coordinator.on_stop)
        self.game_info_signals.is_ready_to_play.connect(
            self.connection_handler.on_ready_to_play
        )
        self.bot_signals.play_harvester.connect(
            self.behavior_coordinator.on_play_harvester
        )
        self.bot_signals.play_fighter.connect(self.behavior_coordinator.on_play_fighter)
        self.bot_signals.play_crafter.connect(self.behavior_coordinator.on_play_crafter)
        self.bot_signals.play_mule_kamas.connect(
            self.behavior_coordinator.on_play_mule_kamas
        )
        self.bot_signals.play_auto_bot.connect(
            self.behavior_coordinator.on_play_auto_bot
        )
        self.bot_signals.play_usable_behavior.connect(
            self.behavior_coordinator.on_play_usable_behavior
        )

    def start(self):
        self.scheduler.start()

    def wait_for_connection_result(self, timeout: float = 120.0) -> bool:
        is_success = self.is_connected_event.wait(timeout)
        return is_success

    def bot_should_not_play(self, now: datetime.datetime):
        if self.from_manual_play.is_set():
            return False
        in_playtime = self.scheduler.is_in_randomized_playtime(now)
        if in_playtime is None:
            return False
        return not in_playtime
