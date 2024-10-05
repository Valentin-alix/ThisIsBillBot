from dataclasses import dataclass

from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.core.frames.frame import Frame
from src.core.modules.harvester import Harvester
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
    # modules
    harvester: Harvester
