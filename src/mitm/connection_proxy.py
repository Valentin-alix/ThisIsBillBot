from dataclasses import dataclass
from typing import Callable

from d3_mapping.protocol.protocol import decode_varint_size, encode_msg
from d3_mapping.protocol.protocol_connection import get_conn_msg_info
from d3_mapping.resources.protos.connection.login_message_pb2 import (
    LoginMessage,
    Request,
)

from src.bot import Bot
from src.mitm.proxy import Proxy, WorkerAction


@dataclass
class ConnectionProxy(Proxy):
    bot: Bot
    on_game_connection_callback: Callable[[tuple[str, int]], int]

    def __post_init__(self):
        super().__post_init__()
        self.bot.event_manager.on_send_callback = self.send_msg

    def alter_msg_datas(
        self, msg_content_datas: bytes, msg_datas: bytes, from_server: bool
    ) -> bytes | None:
        msg = LoginMessage()
        msg.ParseFromString(msg_content_datas)

        if msg.response.HasField("selectServer") and msg.response.selectServer.HasField(
            "success"
        ):
            new_port: int = self.on_game_connection_callback(
                (
                    msg.response.selectServer.success.host,
                    msg.response.selectServer.success.ports[0],
                ),
            )
            msg.response.selectServer.success.host = "localhost"
            msg.response.selectServer.success.ports[0] = new_port
            msg_datas = encode_msg(msg)
        elif msg.response.HasField(
            "identification"
        ) and msg.response.identification.HasField("success"):
            msg.response.identification.success.ClearField(
                "fight_reconnection_server_id"
            )
            msg_datas = encode_msg(msg)

        return msg_datas

    def on_sent_msg_datas(
        self, msg_datas: bytes, was_send_from_proxy: bool, from_server: bool
    ):
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]
        msg_info, msg = get_conn_msg_info(msg_content_datas, from_server)
        self.bot.msg_info_signals.msg_info.emit(msg_info, was_send_from_proxy)
        if msg is not None:
            self.bot.event_manager.process_msg(msg)

    def send_msg(self, msg: Request):
        conn_msg = LoginMessage(request=msg)
        self.queue_worker_item.put(
            (WorkerAction.SEND_SERVER, encode_msg(conn_msg), True, False)
        )
