import random
from dataclasses import dataclass, field
from threading import Timer
from typing import Callable

from db_dofus_unity.protos.connection.login_message_pb2 import LoginMessage, Request
from src.bot import Bot
from src.mitm.proxy import Proxy
from src.protocol.protocol import (
    encode_msg,
    get_conn_msg_info,
    decode_varint_size,
)


@dataclass
class ConnectionProxy(Proxy):
    bot_infos: dict[int, Bot]
    on_game_connection_callback: Callable[[int, tuple[str, int], Bot], None]
    current_bot: Bot | None = field(init=False, default=None)
    _timers: list[Timer] = field(init=False, default_factory=lambda: [])

    def __post_init__(self):
        super().__post_init__()

    def alter_msg_datas(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes:
        msg = LoginMessage()
        msg.ParseFromString(msg_content_datas)

        if msg.response.HasField(
            "identification"
        ) and msg.response.identification.HasField("success"):
            self.current_bot = self.bot_infos[
                msg.response.identification.success.account_id
            ]
            self.current_bot.event_manager.on_send_callback = self.send_msg

        if msg.response.HasField("selectServer") and msg.response.selectServer.HasField(
            "success"
        ):
            if not self.current_bot:
                raise AttributeError("Current account should be defined")

            new_port = random.randint(49152, 65535)

            self.on_game_connection_callback(
                new_port,
                (
                    msg.response.selectServer.success.host,
                    msg.response.selectServer.success.ports[0],
                ),
                self.current_bot,
            )
            msg.response.selectServer.success.host = "localhost"
            msg.response.selectServer.success.ports[0] = new_port
            msg_datas = encode_msg(msg)

        return msg_datas

    def on_sent_msg_datas(self, msg_datas: bytes):
        if not self.current_bot:
            return
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]
        msg_info, msg = get_conn_msg_info(msg_content_datas)
        self.current_bot.msg_info_signals.msg_info.emit(msg_info)
        if msg is not None:
            self.current_bot.event_manager.process_msg(msg)

    def send_msg(self, msg: Request, wait: float | None = None):
        conn_msg = LoginMessage(request=msg)

        def _send_msg():
            self.send_to_server(encode_msg(conn_msg))

        if wait is not None:
            timer = Timer(wait, _send_msg)
            self._timers.append(timer)
            timer.start()
        else:
            _send_msg()
