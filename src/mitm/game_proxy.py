from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol_pb2 import Message as GameMessage
from src.gui.signals.msg_signals import MessageSignals
from src.mitm.proxy import Proxy
from src.protocol import decode_msg, get_game_msg_info


@dataclass
class GameProxy(Proxy):
    msg_signals: MessageSignals

    def handle_msg(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes:
        msg = GameMessage()
        decode_msg(msg, msg_content_datas)
        self.msg_signals.received_msg_info.emit(get_game_msg_info(msg))
        return msg_datas
