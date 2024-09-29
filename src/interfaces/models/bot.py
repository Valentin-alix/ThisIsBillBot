from dataclasses import dataclass

from src.signals.account_signals import AccountSignals
from src.signals.message_signals import MessageInfoSignals
from src.signals.message_event import MessageEvent
from src.modules.harvester import Harvester


@dataclass
class Bot:
    account_nickname: str
    account_signals: AccountSignals
    msg_info_signals: MessageInfoSignals
    msg_signals: MessageEvent
    harvester: Harvester
