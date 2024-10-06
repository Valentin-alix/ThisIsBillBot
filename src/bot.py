from dataclasses import dataclass

from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.frames.frame import Frame
from src.event_manager import EventManager
from src.signals.harvester_signals import HarvesterSignals
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import PlayerSignals, StatePropertySignals


@dataclass
class Bot:
    account: DecipheredApiKey
    # event manager
    event_manager: EventManager
    # signals
    harvester_signals: HarvesterSignals
    player_property_signals: StatePropertySignals
    player_signals: PlayerSignals
    msg_info_signals: MessageInfoSignals
    # frames
    frames: list[Frame]
    # runnable behaviors
    harvester_behavior: HarvesterBehavior
    fighter_behavior: FighterBehavior

    def __post_init__(self):
        self.harvester_signals.play.connect(
            lambda: self.harvester_behavior.start(callback=None, parent=None)
        )
        self.harvester_signals.stop.connect(self.harvester_behavior.stop)
