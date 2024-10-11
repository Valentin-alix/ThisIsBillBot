from dataclasses import dataclass

from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.common.logger import Logger
from src.core.behaviors.farms.fighter.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvest.harvester_behavior import HarvesterBehavior
from src.core.frames.frame import Frame
from src.event_manager import EventManager
from src.interfaces.enums.farm_action_enum import FarmActionEnum
from src.signals.grid_signals import GridSignals
from src.signals.harvester_signals import FarmActionSignals
from src.signals.log_signals import LogSignals
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import WorldSignals


@dataclass
class Bot:
    account: DecipheredApiKey
    # event manager
    event_manager: EventManager
    # signals
    grid_signals: GridSignals
    farm_action_signals: FarmActionSignals
    game_info_signals: GameInfoSignals
    msg_info_signals: MessageInfoSignals
    world_signals: WorldSignals
    log_signals: LogSignals
    # frames
    frames: list[Frame]
    # runnable behaviors
    harvester_behavior: HarvesterBehavior
    fighter_behavior: FighterBehavior
    logger: Logger

    def __post_init__(self):
        self.farm_action_signals.play.connect(self.on_farm_action_play)
        self.farm_action_signals.stop.connect(self.on_farm_action_stop)

    def on_farm_action_play(
        self, farm_action: FarmActionEnum, area_id: int, sub_area_id: int
    ) -> None:
        self.on_farm_action_stop()
        match farm_action:
            case FarmActionEnum.HARVESTER:
                self.harvester_behavior.start(
                    callback=None, parent=None, area_id=area_id, sub_area_id=sub_area_id
                )
            case FarmActionEnum.FIGHTER:
                self.fighter_behavior.start(
                    callback=None, parent=None, area_id=area_id, sub_area_id=sub_area_id
                )
            case _:
                raise ValueError(f"Unhandled farm action : {farm_action}")

    def on_farm_action_stop(self) -> None:
        if self.harvester_behavior.is_running.is_set():
            self.harvester_behavior.stop()
        if self.fighter_behavior.is_running.is_set():
            self.fighter_behavior.stop()
