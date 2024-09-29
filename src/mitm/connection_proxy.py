import random
from dataclasses import dataclass, field
from typing import Callable

from com.ankama.dofus.server.connection.protocol_pb2 import Message as ConnectionMessage

from src.interfaces.models.bot import Bot
from src.mitm.proxy import Proxy

from src.protocol.protocol import decode_msg, encode_msg, get_conn_msg_info


@dataclass
class ConnectionProxy(Proxy):
    account_infos: dict[int, Bot]
    on_game_connection_callback: Callable[[int, tuple[str, int], Bot], None]
    current_account: Bot | None = field(init=False, default=None)

    def handle_msg(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes:
        msg = ConnectionMessage()
        decode_msg(msg, msg_content_datas)

        if msg.response.HasField(
            "identification"
        ) and msg.response.identification.HasField("success"):
            self.current_account = self.account_infos[
                msg.response.identification.success.account_id
            ]
            self.current_account.account_signals.account_is_connected.emit(True)

        if msg.response.HasField("selectServer") and msg.response.selectServer.HasField(
            "success"
        ):
            if not self.current_account:
                raise Exception("Current account should be defined")

            new_port = random.randint(49152, 65535)

            self.on_game_connection_callback(
                new_port,
                (
                    msg.response.selectServer.success.host,
                    msg.response.selectServer.success.ports[0],
                ),
                self.current_account,
            )
            msg.response.selectServer.success.host = "localhost"
            msg.response.selectServer.success.ports[0] = new_port
            msg_datas = encode_msg(msg)

        if self.current_account:
            msg_info, msg = get_conn_msg_info(msg)
            self.current_account.msg_info_signals.message_info.emit(msg_info)
            self.current_account.msg_signals.received_connection_msg.send(msg)

        return msg_datas
