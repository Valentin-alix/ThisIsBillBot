from dataclasses import dataclass
from typing import Callable

from google.protobuf.internal.encoder import _VarintBytes  # type: ignore

from ankama_launcher_emulator.proxy.login_message_pb2 import (
    LoginMessage,
)
from ankama_launcher_emulator.proxy.proxy import Proxy


def _encode_msg(msg: LoginMessage) -> bytes:
    content = msg.SerializeToString()
    return _VarintBytes(len(content)) + content


@dataclass
class ConnectionProxy(Proxy):
    on_game_connection_callback: Callable[[tuple[str, int]], int]

    def alter_msg_datas(
        self, msg_content_datas: bytes, msg_datas: bytes
    ) -> bytes | None:
        msg = LoginMessage()
        msg.ParseFromString(msg_content_datas)

        if msg.response.HasField("selectServer") and msg.response.selectServer.HasField(
            "success"
        ):
            new_port = self.on_game_connection_callback(
                (
                    msg.response.selectServer.success.host,
                    msg.response.selectServer.success.ports[0],
                )
            )
            msg.response.selectServer.success.host = "localhost"
            msg.response.selectServer.success.ports[0] = new_port
            return _encode_msg(msg)

        return msg_datas
