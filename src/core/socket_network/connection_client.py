import threading
from dataclasses import dataclass
from typing import Callable

from google.protobuf.message import Message

from src.const import DOFUS_CONNECTION_URL
from src.core.behaviors.socket.connection_behavior import ConnectionBehavior
from src.core.socket_network.base_client import BaseClient
from src.protocol.protocol import decode_varint_size, encode_msg
from src.protocol.protocol_connection import (
    get_conn_msg,
    get_conn_msg_info,
)

LOGIN_SERVER_PORT = 5555


@dataclass
class ConnectionClient(BaseClient):
    connection_behavior: ConnectionBehavior

    def connect(
        self, game_token: str, callback: Callable[[str | None, str, int, str], None]
    ) -> None:
        """Authenticate against the login server and retrieve game server coordinates."""
        self.client_socket.connect((DOFUS_CONNECTION_URL, LOGIN_SERVER_PORT))
        self.bot.event_manager.on_send_conn_callback = self.send_msg
        self.bot.logger.info(f"Connected to {DOFUS_CONNECTION_URL}:{LOGIN_SERVER_PORT}")
        threading.Thread(target=self.loop, daemon=True).start()
        self.connection_behavior.start(
            game_token=game_token, callback=callback, parent=None
        )

    def send_msg(self, msg: Message) -> None:
        try:
            self.client_socket.sendall(encode_msg(msg))
            msg_info = get_conn_msg_info(msg, False)
            self.bot.msg_info_signals.msg_info.emit(msg_info, True)
        except OSError as err:
            self.bot.logger.error(f"send error: {err}")
            self.close()

    def on_received_msg_datas(self, msg_datas: bytes) -> None:
        size, pos = decode_varint_size(msg_datas)
        msg = get_conn_msg(msg_datas[pos : pos + size])[1]
        self.bot.event_manager.process_msg(msg)
        msg_info = get_conn_msg_info(msg, True)
        self.bot.msg_info_signals.msg_info.emit(msg_info, False)

    def on_close(self) -> None:
        self.bot.event_manager.on_send_conn_callback = None
