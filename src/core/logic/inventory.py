from dataclasses import dataclass, field

from google.protobuf.message import Message

from com.ankama.dofus.server.game.protocol.inventory_pb2 import (
    InventoryContentEvent,
)
from src.signals.message_event import MessageEvent


@dataclass
class Inventory:
    msg_signals: MessageEvent
    kamas: int = field(init=False, default=0)

    def __post_init__(self):
        self.msg_signals.received_game_msg.connect(self.on_received_msg)

    def on_received_msg(self, message: Message):
        if type(message) is InventoryContentEvent:
            self.kamas = message.kamas
