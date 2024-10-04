from dataclasses import dataclass

from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.core.handlers.entity_handler import EntityHandler
from src.core.handlers.interactive_handler import InteractiveHandler
from src.core.handlers.player_handler import PlayerHandler
from src.core.modules.harvester import Harvester
from src.signals.harvester_signals import HarvesterSignals
from src.signals.message_events import MessageEvents
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import PlayerSignals, StatePropertySignals


@dataclass
class Bot:
    account: DecipheredApiKey
    # signals
    harvester_signals: HarvesterSignals
    player_property_signals: StatePropertySignals
    player_signals: PlayerSignals
    msg_info_signals: MessageInfoSignals
    msg_events: MessageEvents
    # handlers
    entity_handler: EntityHandler
    player_handler: PlayerHandler
    interactive_handler: InteractiveHandler
    # modules
    harvester: Harvester
