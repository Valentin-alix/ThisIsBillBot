import random
from dataclasses import dataclass
from typing import Callable

from com.ankama.dofus.server.connection.protocol_pb2 import Message as ConnectionMessage
from src.gui.signals.msg_signals import MessageSignals
from src.mitm.proxy import Proxy
from src.protocol import decode_msg, encode_msg, get_conn_msg_info


@dataclass
class ConnectionProxy(Proxy):
    msg_signals: MessageSignals
    on_game_connection_callback: Callable[[int, tuple[str, int]], None]

    def handle_msg(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes:
        msg = ConnectionMessage()
        decode_msg(msg, msg_content_datas)
        if msg.response.HasField("selectServer"):
            new_port = random.randint(49152, 65535)
            self.on_game_connection_callback(
                new_port,
                (
                    msg.response.selectServer.success.host,
                    msg.response.selectServer.success.ports[0],
                ),
            )
            msg.response.selectServer.success.host = "localhost"
            msg.response.selectServer.success.ports[0] = new_port
            msg_datas = encode_msg(msg)

        self.msg_signals.received_msg_info.emit(get_conn_msg_info(msg))
        return msg_datas
