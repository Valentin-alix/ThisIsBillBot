import random
from dataclasses import dataclass, field
from typing import Callable

from protos.connection.login_message_pb2 import LoginMessage, Request
from src.bot import Bot
from src.mitm.proxy import Proxy, WorkerAction
from src.protocol.protocol import (
    encode_msg,
    decode_varint_size,
)
from src.protocol.protocol_connection import get_conn_msg_info


@dataclass
class ConnectionProxy(Proxy):
    bot_infos: dict[int, Bot]
    on_game_connection_callback: Callable[[int, tuple[str, int], Bot], None]
    bot_identified: Bot | None = field(init=False, default=None)

    def alter_msg_datas(
        self, msg_content_datas: bytes, msg_datas: bytes
    ) -> bytes | None:
        msg = LoginMessage()
        msg.ParseFromString(msg_content_datas)

        if msg.response.HasField(
            "identification"
        ) and msg.response.identification.HasField("success"):
            self.bot_identified = self.bot_infos[
                msg.response.identification.success.account_id
            ]
            self.bot_identified.event_manager.on_send_callback = self.send_msg

        elif msg.response.HasField(
            "selectServer"
        ) and msg.response.selectServer.HasField("success"):
            if not self.bot_identified:
                raise AttributeError("Current account should be defined")

            new_port = random.randint(49152, 65535)

            self.on_game_connection_callback(
                new_port,
                (
                    msg.response.selectServer.success.host,
                    msg.response.selectServer.success.ports[0],
                ),
                self.bot_identified,
            )
            msg.response.selectServer.success.host = "localhost"
            msg.response.selectServer.success.ports[0] = new_port
            msg_datas = encode_msg(msg)

        return msg_datas

    def on_sent_msg_datas(self, msg_datas: bytes, was_send_from_proxy: bool):
        if not self.bot_identified:
            return
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]
        msg_info, msg = get_conn_msg_info(msg_content_datas)
        self.bot_identified.msg_info_signals.msg_info.emit(
            msg_info, was_send_from_proxy
        )
        if msg is not None:
            self.bot_identified.event_manager.process_msg(msg)

    def send_msg(self, msg: Request):
        conn_msg = LoginMessage(request=msg)
        self.queue_worker_item.put(
            (WorkerAction.SEND_SERVER, encode_msg(conn_msg), True)
        )
